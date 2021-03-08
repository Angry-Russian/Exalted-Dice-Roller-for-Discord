import sys, os, re, random, discord, math
from functools import reduce
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO
from dotenv import load_dotenv

load_dotenv('./.env')

#paste in discord token
#invite the bot
#type the below command in discord to roll 10 dice (d10s only for exalted)
#!roll 10

class RollerBot:
    token = os.getenv('DISCORD_TOKEN')
    def __init__(self):
        client = discord.Client()
        @client.event
        async def on_message(message):
            return await self.parse_message(message)
        self.client = client
        client.run(self.token)

    async def parse_message(self, message):
        user = message.author.mention
        content = message.content.lower()
        if message.author == self.client.user:
            return
        elif content == '!roll' or content.startswith('!roll help'):
            await message.channel.send(self.help())
        elif content.startswith('!rolli '):
            print('Rolling as an image for', user, ':', content);
            await message.channel.send(**self.parseAsImage(user, self.roll(content)))
        elif content.startswith('!roll '):
            print('Rolling for', user, ':', content);
            await message.channel.send(**self.parseAsText(user, self.roll(content)))

    def help(self):
        return """```prolog
Usage: `!roll n [options]`

Options (case insensitive):
    `rr`    ReRoll: rerolls matching dice until they cease to appear.
                `!roll 6 rr=1` rerolls 1s until there are none left
                `!roll 6 rr<7` rerolls `{ 1, 2, 3, 4, 5, 6 }` until none are left
                rerolled dice DO NOT contribute to results

    `ro`    Reroll Once: as `rr` but each die is only rerolled once.

    `do`    Double: matching faces are counted as 2 successes instead of 1.
                `!roll 6 do>7` counts 8s, 9s and 10s as double-successes.
                `!roll 6 do=7` counts only 7s as double-successes
                default: `=10`

    `fs`    Faces Subtract: matching faces subtract from accumulated successes.
                `!roll 5 fs<3` would subtract 1s and 2s from successes

    `+N`,   Adds or Subtracts successes to/from the final result, minimum of zero.
    `-N`        `!roll 2 -3` would roll 2 dice and subtract 3 successes from the result.
                `!roll 5 +1` would roll 5 dice and add 1 success to the result.

    `*N`,   Multiplies or Divides the final result by 'N'.
    `/N`        you can specify 'up' or 'dn' for the result to be rounded up or rounded down.
                default: rounded up.

    `stunt` applies a level 1, 2 or 3 stunt to the roll
                `stunt 1` provides  +2 dice
                `stunt 2` provides  +2 dice + 1 success
                `stunt 3` provides  +2 dice + 2 successes

    `damage`    treats roll as a damage roll: 10s are not doubled unless explicitly specified.
```"""


    def toComparator(self, comparer, target):
        target = int(target)
        if comparer == ">" :                       return lambda die: die > target;
        elif comparer == "<" :                     return lambda die: die < target;
        elif comparer == ">=" :                    return lambda die: die >= target;
        elif comparer == "<=" :                    return lambda die: die <= target;
        elif comparer == "=" or comparer == "==" : return lambda die: die == target;
        return lambda die : False;

    def toOperator(self, operator, target, round='up'):
        target = int(target)
        if operator == '-' :   return lambda s: int(s)-int(target);
        elif operator == '+' : return lambda s: int(s)+int(target);
        elif operator == '*' : return lambda s: int(s)*int(target);
        elif operator == '/' :
            if round == 'dn' : return lambda s: math.floor(int(s)/int(target));
            else :             return lambda s: math.ceil(int(s)/int(target));
        else :                 return lambda s: s

    def remap(self, regexMatch, default):
        if regexMatch is None : return default
        return regexMatch.groups()

    def dec(self, text, d, applyDecoration=True):
        return d+str(text)+d if applyDecoration is True else str(text)

    def roll(self, options):
        try:
            options = options.split(' ', 2)
            command = options.pop(0)
            dice = int(options.pop(0))
            if len(options) > 0 :
                options = options[0]
            else :
                options = ''

        except:
            return "Unexpected error occured"

        if dice >200:
            return "That's too many dice, my dude!"


        damage = re.search(r'(damage)', options) is not None
        stunt = re.search(r'(?<=stunt)\ ?(1|2|3)', options)
        stunt = int(stunt.group(1)) if stunt is not None else 0;
        t = re.search(r'(?<=t)(\d+)', options)
        t = int(t.group(1)) if t is not None else 7;

        rr = self.toComparator(*self.remap(re.search(r'(?<=rr)([<>=]=?)(\d+)', options), ('=', 0)))
        ro = self.toComparator(*self.remap(re.search(r'(?<=ro)([<>=]=?)(\d+)', options), ('=', 0)))
        fs = self.toComparator(*self.remap(re.search(r'(?<=fs)([<>=]=?)(\d+)', options), ('=', 0)))
        do = self.toComparator(*self.remap(re.search(r'(?<=do)([<>=]=?)(\d+)', options), ('=', 10 if damage is False else 0)))
        t =  self.toComparator('>=', t)

        result_add = self.toOperator(*self.remap(re.search(r'(\+)(\d+)', options), ('=', 0)))
        result_sub = self.toOperator(*self.remap(re.search(r'(\-)(\d+)', options), ('=', 0)))
        result_mul = self.toOperator(*self.remap(re.search(r'(\*)(\d+)', options), ('=', 0)))
        result_div = self.toOperator(*self.remap(re.search(r'(\/)(\d+)(dn|up)?', options), ('=', 0)))

        count = int(dice + 2 if stunt > 0 else dice)
        results = []
        success = max(0, stunt - 1)

        for x in range(count):
            result = random.randrange(1,11)
            rerollOnce =  ro(result)

            while rerollOnce or rr(result):
                rerollOnce = False
                results.append(self.dec(result, '~~'))
                result = random.randrange(1,11)

            succ = t(result)
            double = do(result)
            subtract = fs(result)

            results.append(self.dec(self.dec(result, '**', double or damage and succ), '__', succ))

            if succ : success +=1;
            if double : success +=1;
            if subtract : success -=1;

        success = max(0, reduce(lambda total, function: function(total), [
            result_mul,
            result_div,
            result_add,
            result_sub,
        ], success))

        added = result_sub(result_add(0))
        return (count, results, success, added, stunt)

    def parseAsText(self, user, rollResult):
        (count, results, success, added, stunt) = rollResult

        msg = "%s rolled %d dice for %d success%s%s\nroll: [ %s ]%s" % (
            user,
            count,
            success,
            '' if success == 1 else 'es',
            ', bummer!' if success <= 0 else '.',
            ', '.join(results),
            ((' %+ds' % added) if added != 0 else '' ) +
            ((' %+ds from stunt' % (stunt-1)) if stunt > 0 else '')
        )

        if '1' in results and success == 0:
            msg = msg + '\n**Critical Fail**'

        return {
            'content': msg
        }

    def parseAsImage(self, user, rollResult):
        (count, results, success, added, stunt) = rollResult

        scale = 128;
        cols = min(10, len(results))
        rows = math.ceil(len(results) / cols)

        img = Image.new('RGBA', (cols*scale, rows*scale), (0, 0, 0, 0))
        die = Image.open('images/Regular D10.png')
        dieBB = die.getbbox();

        aspectRatio = float(dieBB[2])/float(dieBB[3])
        size = (scale, round(scale / aspectRatio))
        if (aspectRatio < 1) :
            size = (round(scale * aspectRatio), scale)
        die = die.resize(size)
        padding = (int((scale - size[0])/2), int((scale-size[1])/2))

        canvas = ImageDraw.Draw(img)
        font = ImageFont.truetype('fonts/Ubuntu Mono derivative Powerline.ttf', int(scale/2))
        for r in range(len(results)) :
            result = results[r]
            x = (r % cols) * scale
            y = math.floor(r / cols) * scale
            crit = '**' in result
            succ = '__' in result
            discard = '~~' in result

            face = re.search(r'(\d+)', result).group(1)
            dieCopy = die.copy()
            fill = (0, 0, 0, 255)

            if discard :
                fill = (255, 0, 0, 64)
                ImageDraw.Draw(dieCopy).line((0, 0) + size, fill=fill, width=int(scale/32))
                ImageDraw.Draw(dieCopy).line((0, size[1], size[0], 0), fill=fill, width=int(scale/32))
                dieCopy.putalpha(128)
            elif crit :
                fill = (255, 255, 0, 255)
            elif succ :
                fill = (255, 128, 0, 255)

            img.paste(dieCopy, (x + padding[0], y + padding[1]), die)
            # img.alpha_composite(dieCopy, (x, y))
            canvas.text((x + scale/2, y + scale/2), face, fill=fill, font=font, anchor='mm')

        with BytesIO() as rollImage:
            img.save(rollImage, 'PNG')
            rollImage.seek(0)
            return {
                'content' : '%s rolls %d dice, getting %d success%s!' % (user, count, success, 'es' if success != 1 else ''),
                'file' : discord.File(fp=rollImage, filename='result.png')
            }

if __name__ == "__main__":
    roller = RollerBot();