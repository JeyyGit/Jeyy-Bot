import asyncio
import os
from io import BytesIO

from jishaku.functools import executor_function
from PIL import Image


@executor_function
def to_jpg(im):
    img = Image.open(im)
    canv = Image.new('RGB', img.size, 'white')
    canv.paste(img, (0, 0))

    buf = BytesIO()
    canv.save(buf, 'PNG')
    buf.seek(0)

    return buf

async def get_locket(image, image_2 = None):
    tmp_name = os.urandom(16).hex()
    image = await to_jpg(image)

    command = [
        'cd', 'makesweet/', '&&', 'sudo', 'docker', 
        'run', '-v', '\"$(pwd):/share\"', 'paulfitz/makesweet',
        '--zip', 'templates/heart-locket.zip', 
        '--in', f'tmp/image/{tmp_name}.png',
        '--gif', f'tmp/result/{tmp_name}.gif'
    ]

    with open(f'makesweet/tmp/image/{tmp_name}.png', "wb") as f:
        f.write(image.getbuffer())

    if image_2:
        tmp_name_2 = os.urandom(16).hex()
        image_2 = await to_jpg(image_2)

        command.insert(13, f'tmp/image/{tmp_name_2}.png')

        with open(f'makesweet/tmp/image/{tmp_name_2}.png', "wb") as f:
            f.write(image_2.getbuffer())

    proc = await asyncio.subprocess.create_subprocess_shell(' '.join(command),
        stdout=asyncio.subprocess.PIPE, 
        stderr=asyncio.subprocess.PIPE
    )
    
    await proc.wait()
    with open(f'makesweet/tmp/result/{tmp_name}.gif', "rb") as fh:
        buf = BytesIO(fh.read())

    os.remove(f'makesweet/tmp/image/{tmp_name}.png')
    os.remove(f'makesweet/tmp/result/{tmp_name}.gif')

    if image_2:
        os.remove(f'makesweet/tmp/image/{tmp_name_2}.png')

    return buf
        

async def get_billboard(image):
    tmp_name = os.urandom(16).hex()
    image = await to_jpg(image)

    command = [
        'cd', 'makesweet/', '&&', 'sudo', 'docker', 
        'run', '-v', '\"$(pwd):/share\"', 'paulfitz/makesweet',
        '--zip', 'templates/billboard-cityscape.zip', 
        '--in', f'tmp/image/{tmp_name}.png',
        '--gif', f'tmp/result/{tmp_name}.gif'
    ]

    with open(f'makesweet/tmp/image/{tmp_name}.png', "wb") as f:
        f.write(image.getbuffer())

    proc = await asyncio.subprocess.create_subprocess_shell(' '.join(command),
        stdout=asyncio.subprocess.PIPE, 
        stderr=asyncio.subprocess.PIPE
    )
    
    await proc.wait()
    with open(f'makesweet/tmp/result/{tmp_name}.gif', "rb") as fh:
        buf = BytesIO(fh.read())

    os.remove(f'makesweet/tmp/image/{tmp_name}.png')
    os.remove(f'makesweet/tmp/result/{tmp_name}.gif')

    return buf

async def get_flag(image):
    tmp_name = os.urandom(16).hex()
    image = await to_jpg(image)

    command = [
        'cd', 'makesweet/', '&&', 'sudo', 'docker', 
        'run', '-v', '\"$(pwd):/share\"', 'paulfitz/makesweet',
        '--zip', 'templates/flag.zip', 
        '--in', f'tmp/image/{tmp_name}.png',
        '--gif', f'tmp/result/{tmp_name}.gif'
    ]

    with open(f'makesweet/tmp/image/{tmp_name}.png', "wb") as f:
        f.write(image.getbuffer())

    proc = await asyncio.subprocess.create_subprocess_shell(' '.join(command),
        stdout=asyncio.subprocess.PIPE, 
        stderr=asyncio.subprocess.PIPE
    )
    
    await proc.wait()
    with open(f'makesweet/tmp/result/{tmp_name}.gif', "rb") as fh:
        buf = BytesIO(fh.read())

    os.remove(f'makesweet/tmp/image/{tmp_name}.png')
    os.remove(f'makesweet/tmp/result/{tmp_name}.gif')

    return buf