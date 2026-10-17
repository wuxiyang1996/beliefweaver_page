"""Render the BeliefWeaver explainer from original motion graphics and local TTS.

Install requirements.txt, then run with Python 3.12+ on Windows. The temporary
work directory is explicit; only the MP4, VTT, and poster enter the website.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import textwrap
import wave

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg


W, H, FPS = 1280, 720, 30
BG = "#f7f7f2"
INK = "#12202d"
MUTED = "#5e6d76"
TEAL = "#087e8b"
INDIGO = "#5b5fc7"
GOLD = "#c39c4a"
LINE = "#d7dfdc"
PALE_TEAL = "#e6f1ef"
PALE_INDIGO = "#ececf7"
WHITE = "#ffffff"
RED = "#b75850"
FONT_DIR = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
FONTS = {}


def font(size, bold=False):
    key = size, bold
    if key not in FONTS:
        candidates = [FONT_DIR / ("segoeuib.ttf" if bold else "segoeui.ttf")]
        candidates += [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
                            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]
        found = next((p for p in candidates if p.exists()), None)
        if found is None:
            raise FileNotFoundError("Install Segoe UI or DejaVu Sans fonts")
        FONTS[key] = ImageFont.truetype(str(found), size)
    return FONTS[key]


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def txt(draw, xy, s, size=24, color=INK, bold=False, anchor=None):
    draw.text(xy, s, font=font(size, bold), fill=color, anchor=anchor)


def fitted(draw, xy, text, max_width, size=24, **kwargs):
    while draw.textlength(text, font=font(size, kwargs.get("bold", False))) > max_width:
        size -= 1
    txt(draw, xy, text, size=size, **kwargs)


def wrap(draw, text, width, size=26, bold=False):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        if line and draw.textlength(test, font=font(size, bold)) > width:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)
    return lines


def card(draw, box, fill=WHITE, border=LINE, radius=18, width=2):
    draw.rounded_rectangle(box, radius, fill=fill, outline=border, width=width)


def pill(draw, x, y, text, color=TEAL, bg=PALE_TEAL, size=17):
    width = draw.textlength(text, font=font(size, True)) + 28
    card(draw, (x, y, x + width, y + 33), fill=bg, border=bg, radius=16)
    txt(draw, (x + 14, y + 5), text, size, color, True)
    return width


def dot(draw, x, y, radius=5, color=TEAL):
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def arrow(draw, start, end, color=LINE, width=3, progress=1):
    x0, y0 = start
    x1, y1 = end
    x1 = x0 + (x1 - x0) * progress
    y1 = y0 + (y1 - y0) * progress
    draw.line((x0, y0, x1, y1), fill=color, width=width)
    angle = math.atan2(y1 - y0, x1 - x0)
    a = 10
    draw.polygon([(x1, y1), (x1-a*math.cos(angle-.55), y1-a*math.sin(angle-.55)),
                  (x1-a*math.cos(angle+.55), y1-a*math.sin(angle+.55))], fill=color)


def particle(draw, a, b, t, phase=0, color=TEAL, speed=.25):
    p = (t * speed + phase) % 1
    dot(draw, a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p, 5, color)


def check(draw, x, y, color=TEAL, size=15):
    draw.line([(x-size*.55,y), (x-size*.12,y+size*.45), (x+size*.7,y-size*.5)],
              fill=color, width=4)


def cross(draw, x, y, color=RED, size=9):
    draw.line((x-size,y-size,x+size,y+size), fill=color, width=3)
    draw.line((x-size,y+size,x+size,y-size), fill=color, width=3)


def chrome(draw, index, t, duration, total):
    # Small graph mark, persistent branding, chapter progress.
    draw.line((73,40,87,31,98,45,73,40), fill=TEAL, width=2)
    for x,y in [(73,40),(87,31),(98,45)]:
        dot(draw,x,y,3,TEAL)
    txt(draw,(112,26),"BELIEFWEAVER",20,INK,True)
    txt(draw,(1207,31),"RESEARCH OVERVIEW  /  arXiv:2610.18082",15,MUTED,anchor="ra")
    draw.line((72,78,1208,78), fill=LINE, width=1)
    for i in range(6):
        x = 72 + i * 190
        draw.rounded_rectangle((x,91,x+170,95),2,fill=LINE)
        p = 1 if i < index else (ease(t / duration) if i == index else 0)
        if p:
            draw.rounded_rectangle((x,91,x+170*p,95),2,fill=TEAL)


def title(draw, heading, subheading):
    fitted(draw,(72,124),heading,1136,44,bold=True)
    txt(draw,(74,184),subheading,23,MUTED)


def schematic(draw):
    txt(draw,(1206,586),"SCHEMATIC ANIMATION",13,MUTED,anchor="ra")


def failure(draw,t,duration):
    title(draw,"Failure shouldn’t erase evidence.","Long-horizon agents need recovery that learns.")
    for i in range(3):
        x=72+i*390
        reveal=ease((t-i*.65)/.8)
        y=270+int((1-reveal)*28)
        card(draw,(x,y,x+354,y+224),border=LINE)
        pill(draw,x+22,y+20,f"ATTEMPT 0{i+1}",color=MUTED,bg="#eef0ec",size=16)
        txt(draw,(x+24,y+77),"Execute a repair",27,INK,True)
        txt(draw,(x+24,y+119),"Check → fail → roll back",21,MUTED)
        # Repeating progress and failure are deliberately illustrative.
        p=(t*.23-i*.18)%1
        draw.rounded_rectangle((x+24,y+173,x+286,y+183),5,fill="#e7e9e5")
        draw.rounded_rectangle((x+24,y+173,x+24+262*min(.87,p*1.3),y+183),5,fill=INDIGO)
        cross(draw,x+316,y+178,size=9)
        if i<2:
            arrow(draw,(x+361,y+112),(x+382,y+112),MUTED,2)
    txt(draw,(640,541),"What if the next attempt could keep what the last one learned?",24,TEAL,True,anchor="ma")
    schematic(draw)


def belief(draw,t,duration):
    title(draw,"Keep evidence. Update belief.","A persistent relational state connects attempts, including rollbacks.")
    for i in range(3):
        y=260+i*94
        fill=PALE_TEAL if (int(t/1.9)%3)==i else WHITE
        card(draw,(72,y,359,y+76),fill=fill,border=LINE)
        txt(draw,(94,y+13),["Attempt 01","Rollback","Attempt 02"][i],21,INK,True)
        txt(draw,(94,y+44),["New observations","Execution state restored","Evidence retained"][i],17,MUTED)
        if i<2: arrow(draw,(214,y+77),(214,y+91),MUTED,2)
    arrow(draw,(379,388),(454,388),TEAL,3)
    particle(draw,(379,388),(454,388),t,color=TEAL,speed=.4)
    center=(821,386)
    nodes=[(605,277,"Repair hypotheses",INDIGO),(1038,277,"Attempts",TEAL),
           (605,489,"Observations",TEAL),(1038,489,"Checkpoints",GOLD)]
    # Edges and particles preserve a visible cumulative graph.
    for i,(x,y,label,c) in enumerate(nodes):
        draw.line((x,y,*center),fill=LINE,width=3)
        particle(draw,(x,y),center,t,phase=i*.23,color=c,speed=.2)
    draw.line((605,277,1038,277,1038,489,605,489,605,277),fill=LINE,width=2)
    for i,(x,y,label,c) in enumerate(nodes):
        bob=math.sin(t*.9+i)*3
        card(draw,(x-100,y-32+bob,x+100,y+32+bob),border=c,fill=WHITE,radius=16)
        fitted(draw,(x,y-16+bob),label,176,21,color=c,bold=True,anchor="ma")
    halo=67+3*math.sin(t*1.8)
    draw.ellipse((center[0]-halo,center[1]-halo,center[0]+halo,center[1]+halo),fill=PALE_TEAL)
    draw.ellipse((center[0]-57,center[1]-57,center[0]+57,center[1]+57),fill=TEAL)
    txt(draw,(821,362),"BELIEF",22,WHITE,True,anchor="ma")
    txt(draw,(821,395),"STATE",17,WHITE,anchor="ma")
    pill(draw,731,548,"Evidence persists",size=17)
    schematic(draw)


def recovery(draw,t,duration):
    title(draw,"Reason before the next action.","Repair hypotheses meet a diagnostic gate before execution.")
    labels=[("Imagine","Propose repairs",INDIGO),("Assess","Compare hypotheses",INDIGO),
            ("Diagnose","Seek evidence",TEAL),("Gate","Decide to proceed",TEAL),
            ("Execute","Observe outcomes",GOLD)]
    for i,(name,sub,c) in enumerate(labels):
        x=72+i*232
        active=int(t/.85)%5==i
        card(draw,(x,283,x+208,414),fill=PALE_TEAL if active else WHITE,border=c if active else LINE,width=2)
        txt(draw,(x+20,303),f"0{i+1}",16,c,True)
        txt(draw,(x+20,333),name,26,INK,True)
        fitted(draw,(x+20,376),sub,170,17,color=MUTED)
        if i<4:
            arrow(draw,(x+209,348),(x+230,348),TEAL,2)
            particle(draw,(x+210,348),(x+229,348),t,phase=i*.2,speed=.65)
    # A feedback loop returns observations to persistent belief.
    draw.line((1104,418,1104,507,177,507,177,418),fill=TEAL,width=3,joint="curve")
    arrow(draw,(177,459),(177,418),TEAL,3)
    p=(t*.14)%1
    dot(draw,1104-927*p,507,6,TEAL)
    card(draw,(420,482,864,535),fill=BG,border=BG,radius=8)
    txt(draw,(642,493),"Update belief with new evidence",22,TEAL,True,anchor="ma")
    txt(draw,(640,552),"After rollback, execution resets; learned evidence remains.",19,MUTED,anchor="ma")
    schematic(draw)


def student(draw,t,duration):
    title(draw,"Distill recurring reasoning.","A 9B student learns four roles through SFT, then OPD.")
    card(draw,(72,266,358,526),fill=WHITE,border=INDIGO)
    pill(draw,97,288,"TEACHER",INDIGO,PALE_INDIGO,16)
    txt(draw,(97,341),"BeliefWeaver",31,INK,True)
    txt(draw,(97,391),"Reasoning traces",21,MUTED)
    txt(draw,(97,427),"Teacher feedback",21,MUTED)
    stages=[(459,329,"SFT","Supervised fine-tuning"),(459,444,"OPD","On-policy distillation")]
    for i,(x,y,label,sub) in enumerate(stages):
        arrow(draw,(377,y+7),(431,y+7),INDIGO,3)
        particle(draw,(377,y+7),(431,y+7),t,color=INDIGO,speed=.45)
        card(draw,(x,y-30,x+290,y+47),fill=PALE_INDIGO,border=PALE_INDIGO,radius=15)
        txt(draw,(x+20,y-20),label,26,INDIGO,True)
        txt(draw,(x+20,y+17),sub,17,MUTED)
        txt(draw,(x+261,y-16),f"0{i+1}",17,INDIGO,True,anchor="ra")
        if i==1:
            arrow(draw,(769,y+7),(822,y+7),TEAL,3)
            particle(draw,(769,y+7),(822,y+7),t,phase=.5,color=TEAL,speed=.45)
    arrow(draw,(604,381),(604,409),INDIGO,3)
    particle(draw,(604,381),(604,409),t,color=INDIGO,speed=.45)
    card(draw,(846,266,1208,526),fill=PALE_TEAL,border=TEAL)
    txt(draw,(873,283),"9B",61,TEAL,True)
    txt(draw,(984,309),"STUDENT",19,TEAL,True)
    labels=["Probe generation","Evidence judgment","Frontier-relation inference","Task-clause assessment"]
    for i,label in enumerate(labels):
        y=379+i*31
        check(draw,883,y+10,size=10)
        txt(draw,(908,y-3),label,19,INK)
    txt(draw,(640,561),"Generation is a separate student variant.",19,MUTED,anchor="ma")
    schematic(draw)


def results(draw,t,duration):
    title(draw,"Paper-reported results on 113 tasks.","Overall final score · 65 TB2 + 23 TB3 + 25 LHTB")
    rows=[("Terminus-2",48.6,MUTED),("BeliefWeaver",53.7,TEAL),("SFT + OPD",58.4,INDIGO)]
    start=343
    chart_width=660
    # Zero-based axis: results are not visually exaggerated.
    for tick in [0,20,40,60]:
        x=start+chart_width*tick/60
        draw.line((x,260,x,487),fill=LINE,width=1)
        txt(draw,(x,492),f"{tick}%",16,MUTED,anchor="ma")
    for i,(name,score,c) in enumerate(rows):
        y=271+i*77
        txt(draw,(72,y+10),name,27,INK,True)
        p=ease((t-.35-i*.35)/1.6)
        bw=chart_width*score/60*p
        if bw>1: draw.rounded_rectangle((start,y,start+bw,y+49),7,fill=c)
        txt(draw,(start+bw+17,y+5),f"{score:.1f}%",29,c,True)
    pill(draw,72,542,"+5.1 pp teacher",TEAL,PALE_TEAL,18)
    pill(draw,302,542,"+9.8 pp student",INDIGO,PALE_INDIGO,18)
    txt(draw,(1208,543),"vs. native Terminus-2 baseline",17,MUTED,anchor="ra")
    txt(draw,(1208,580),"Source: paper Table 1 · reported, not independently reproduced",15,MUTED,anchor="ra")


def ending(draw,t,duration):
    # Live graph keeps the closing card moving without distracting from the title.
    points=[]
    for i in range(6):
        a=2*math.pi*i/6+t*.035
        points.append((1015+147*math.cos(a),361+147*math.sin(a)))
    for i in range(6):
        for j in [1,2]:
            b=points[(i+j)%6]
            draw.line((*points[i],*b),fill=LINE,width=2)
        particle(draw,points[i],points[(i+2)%6],t,phase=i/6,color=TEAL,speed=.16)
        dot(draw,*points[i],10,TEAL if i%2 else INDIGO)
    draw.ellipse((949,295,1081,427),fill=PALE_TEAL)
    txt(draw,(1015,337),"BW",38,TEAL,True,anchor="ma")
    pill(draw,72,157,"FAILURE RECOVERY THROUGH BELIEF UPDATES",size=15)
    txt(draw,(72,225),"BeliefWeaver",67,INK,True)
    txt(draw,(76,328),"Let evidence survive failure.",33,TEAL,True)
    txt(draw,(76,403),"Persistent belief. Grounded recovery.",25,MUTED)
    txt(draw,(76,474),"Read the paper",20,INK,True)
    txt(draw,(76,510),"arxiv.org/abs/2610.18082",27,INDIGO)
    txt(draw,(1208,586),"SYNTHETIC NARRATION · ORIGINAL SCHEMATIC GRAPHICS",12,MUTED,anchor="ra")


SCENES=[failure,belief,recovery,student,results,ending]


def timecode(seconds):
    ms=round(seconds*1000)
    h,ms=divmod(ms,3600000)
    m,ms=divmod(ms,60000)
    s,ms=divmod(ms,1000)
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"


def build_audio(items,work):
    speech=work/"speech"
    waves=[]
    params=None
    for i,item in enumerate(items):
        with wave.open(str(speech/f"speech-{i:02}.wav"),"rb") as src:
            if params is None: params=src.getparams()
            if (src.getnchannels(),src.getsampwidth(),src.getframerate()) != (params.nchannels,params.sampwidth,params.framerate):
                raise ValueError("Narration WAV formats differ")
            waves.append((src.readframes(src.getnframes()),src.getnframes()/src.getframerate()))
    rate=params.framerate
    stride=params.nchannels*params.sampwidth
    frames=[]
    cursor=0.0
    captions=[]
    scene_ranges=[]
    current=0
    scene_start=0.0
    def silence(seconds):
        nonlocal cursor
        n=round(seconds*rate)
        frames.append(b"\0"*(n*stride))
        cursor+=n/rate
    silence(.4)
    for i,(item,(raw,duration)) in enumerate(zip(items,waves)):
        if item["scene"]!=current:
            silence(.35)
            scene_ranges.append((current,scene_start,cursor))
            scene_start=cursor
            current=item["scene"]
            silence(.15)
        captions.append({"start":cursor,"end":cursor+duration,"text":item["caption"],"scene":item["scene"]})
        frames.append(raw)
        cursor+=duration
        silence(.12)
    silence(1)
    # Quantize duration to a video frame boundary.
    silence(math.ceil(cursor*FPS)/FPS-cursor)
    scene_ranges.append((current,scene_start,cursor))
    path=work/"narration.wav"
    with wave.open(str(path),"wb") as out:
        out.setnchannels(params.nchannels)
        out.setsampwidth(params.sampwidth)
        out.setframerate(rate)
        out.writeframes(b"".join(frames))
    return path,captions,scene_ranges,cursor


def render_frame(time,captions,ranges,total,with_captions=True):
    index,start,end=next((r for r in ranges if r[1]<=time<r[2]),ranges[-1])
    local=time-start
    im=Image.new("RGB",(W,H),BG)
    draw=ImageDraw.Draw(im)
    chrome(draw,index,local,end-start,total)
    SCENES[index](draw,local,end-start)
    if with_captions:
        draw.rectangle((0,622,W,H),fill=INK)
        caption=next((c["text"] for c in captions if c["start"]<=time<c["end"]),"")
        lines=wrap(draw,caption,W-150,27)
        y=641 if len(lines)>1 else 657
        for line in lines:
            txt(draw,(640,y),line,27,WHITE,anchor="ma")
            y+=35
        draw.rectangle((0,717,W*(time/total),720),fill=TEAL)
    return im


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir",type=Path,required=True)
    parser.add_argument("--out-dir",type=Path,default=Path(__file__).resolve().parents[1]/"assets")
    parser.add_argument("--synthesize",action="store_true",help="Regenerate WAV segments with Windows System.Speech")
    parser.add_argument("--preview-only",action="store_true",help="Build audio, VTT, poster and contact sheet without encoding MP4")
    args=parser.parse_args()
    work=args.work_dir.resolve()
    out=args.out_dir.resolve()
    work.mkdir(parents=True,exist_ok=True)
    out.mkdir(parents=True,exist_ok=True)
    src=Path(__file__).resolve().parent
    items=json.loads((src/"narration.json").read_text(encoding="utf-8"))
    if args.synthesize:
        subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(src/"synthesize.ps1"),
                        "-Narration",str(src/"narration.json"),"-Output",str(work/"speech"),"-Rate","1"],check=True)
    audio,captions,ranges,total=build_audio(items,work)
    vtt="WEBVTT\n\n"+"\n\n".join(f"{i+1}\n{timecode(c['start'])} --> {timecode(c['end'])}\n{c['text']}"
                                        for i,c in enumerate(captions))+"\n"
    (out/"beliefweaver-short.vtt").write_text(vtt,encoding="utf-8",newline="\n")
    # Closing hero is also the poster; no caption bar on the page preview.
    poster=render_frame(ranges[-1][1]+2,captions,ranges,total,with_captions=False)
    poster.save(out/"video-poster.jpg",quality=95,optimize=True)
    contact=Image.new("RGB",(1280,1080),"#e8e8e3")
    for i,(idx,start,end) in enumerate(ranges):
        still=render_frame(start+(end-start)*.55,captions,ranges,total)
        still.save(work/f"frame-{i+1}.png")
        contact.paste(still.resize((640,360),Image.Resampling.LANCZOS),((i%2)*640,(i//2)*360))
    contact.save(work/"contact-sheet.jpg",quality=93)
    (work/"timing.json").write_text(json.dumps({"duration":total,"scenes":ranges,"captions":captions},indent=2),encoding="utf-8")
    print(json.dumps({"duration":total,"fps":FPS,"resolution":[W,H],"scenes":ranges}),flush=True)
    if args.preview_only: return
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    output=out/"beliefweaver-short.mp4"
    command=[ffmpeg,"-hide_banner","-y","-f","rawvideo","-vcodec","rawvideo","-s",f"{W}x{H}","-pix_fmt","rgb24",
             "-r",str(FPS),"-i","-","-i",str(audio),"-map","0:v","-map","1:a","-c:v","libx264","-preset","medium",
             "-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-ar","48000","-movflags","+faststart",
             "-metadata","title=BeliefWeaver: Evidence survives failure","-metadata","comment=Paper-reported results; synthetic narration; schematic animation.",
             "-shortest",str(output)]
    log=work/"encode.log"
    with log.open("wb") as stream:
        proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=stream)
        try:
            for i in range(math.ceil(total*FPS)):
                im=render_frame(i/FPS,captions,ranges,total)
                proc.stdin.write(im.tobytes())
                if i%300==0: print(f"Rendered {i/FPS:.0f}s / {total:.1f}s",flush=True)
            proc.stdin.close()
            code=proc.wait()
        except BaseException:
            proc.kill()
            proc.wait()
            raise
    if code:
        raise RuntimeError(f"ffmpeg exited {code}; see {log}")
    verify=subprocess.run([ffmpeg,"-hide_banner","-i",str(output),"-f","null","-"],capture_output=True,text=True)
    (work/"verification.txt").write_text(verify.stderr,encoding="utf-8")
    if verify.returncode: raise RuntimeError("MP4 decode verification failed")
    print(json.dumps({"output":str(output),"bytes":output.stat().st_size,"duration":total,"decode_verified":True}),flush=True)


if __name__=="__main__":
    main()
