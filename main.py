import sys, os, getopt, re, random, discord, math
from functools import reduce
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from dotenv import load_dotenv

if(os.getenv('DISCORD_TOKEN') is None):
    load_dotenv('./.env')

class RollerBot(discord.Client):
    token = os.getenv('DISCORD_TOKEN')
    prefix = ".r"

    def __init__(self, randrange=random.randrange):
        super().__init__()
        self.randrange = randrange

    async def start(self):
        await super().start(self.token)

    async def stop(self):
        await super().logout()

    async def on_message(self, message):
        user = message.author.mention
        content = message.content.lower()
        if message.author == self.user:
            pass
        elif content == self.prefix or content.startswith('%s help' % self.prefix):
            await message.channel.send(self.help())
        elif content == '%s shutdown' % self.prefix:
            await message.channel.send('shutting down')
            await self.stop()
        elif content.startswith(self.prefix + 'i'):
            print('Rolling as an image for', user, ':', content)
            await message.channel.send(**self.parseAsImage(user, self.roll(content)))
        elif content.startswith(self.prefix):
            print('Rolling for', user, ':', content)
            await message.channel.send(**self.parseAsText(user, self.roll(content)))

    def help(self):
        print ('fetching help file')
        with open('help/usage.md', 'r') as helpfile :
            return helpfile.read()

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
        options = options.split(' ', 2)
        command = options.pop(0)
        dice = int(options.pop(0))
        if len(options) > 0 :
            options = options[0]
        else :
            options = ''

        if dice > 200:
            return "That's too many dice, my dude!"

        damage = re.search(r'(damage)', options) is not None
        stunt = re.search(r'(?<=stunt)\ ?(1|2|3)', options)
        stunt = int(stunt.group(1)) if stunt is not None else 0;
        t = re.search(r'(?<=tn)(\d+)', options)
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
            result = self.randrange(1,11)
            rerollOnce =  ro(result)

            while rerollOnce or rr(result):
                rerollOnce = False
                results.append(self.dec(result, '~~'))
                result = self.randrange(1,11)

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

        msg = "%s rolled %d dice for %d success%s%s\nroll:\n[ %s ]%s" % (
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
        font = ImageFont.truetype('fonts/UbuntuMono-Regular.ttf', int(scale/2))
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
            canvas.text((x + scale/2, y + scale/2 - int(scale/16)), face, fill=fill, font=font, anchor='mm')

        with BytesIO() as rollImage:
            img.save(rollImage, 'PNG')
            rollImage.seek(0)
            return {
                'content' : '%s rolls %d dice, getting %d success%s!' % (user, count, success, 'es' if success != 1 else ''),
                'file' : discord.File(fp=rollImage, filename='result.png')
            }


if __name__ == "__main__":
    roller = RollerBot();

    options = []
    try:
        options = getopt.getopt(sys.argv[1:], "dur:i:c:")
    except getopt.GetoptError as error:
        print(error)
        raise SystemExit

    if len(options[0]) == 0:
        print("""
        No commands passed, nothing to do. If you're running this as a build command, try adding something like '-r "8 stunt 1"'.
        """)
        raise SystemExit;

    username = 'You'
    def setUser(u):
        global username
        username = u
        return 'Setting username to %s' % u

    daemonize = False
    def setDaemonize(*args):
        global daemonize
        daemonize = True
        return 'Running daemon after all commands'

    actions = {
        '-u': setUser,
        '-d': setDaemonize,
        '-r': lambda x: roller.parseAsText(username, roller.roll(roller.prefix + ' ' + x))['content'],
        '-i': lambda x: roller.parseAsImage(username, roller.roll(roller.prefix + 'i ' + x))['content'],
        '-c': lambda x: (
            roller.parseAsImage(username, roller.roll(x)) if x.startswith(proller.prefix + 'i ')
            else roller.parseAsText(username, roller.roll(x)) if x.startswith(roller.prefix + ' ')
            else {'content' : 'command must be "roll" or "rolli"'}
        )['content'],
    }

    for option in options[0]:
        result = actions.get(option[0], lambda x: '... skipping %s ...' % option[0])
        print(result(option[1]))

    if(daemonize):
        roller.run()
