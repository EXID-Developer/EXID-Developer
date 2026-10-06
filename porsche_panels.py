"""Render photographed instrument panels with accessible, code-rendered content.
Statistics are explicitly dated snapshots, never fabricated live counters.
"""
from pathlib import Path
from html import escape
import base64
OUT=Path(__file__).resolve().parent/'assets'/'porsche'
def text(x,y,value,size=22,color='#eff0f2',extra=''):
 return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" {extra}>{escape(str(value))}</text>'
def build_panels():
 from porsche import effects
 material=base64.b64encode((OUT/'panel-material.webp').read_bytes()).decode()
 def panel(name,title,body):
  s=f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500" viewBox="0 0 900 500" role="img"><title>{escape(title)}</title><image href="data:image/webp;base64,{material}" width="900" height="600" y="-50"/><g font-family="Arial,Helvetica,sans-serif">{body}</g>{effects(0,0,900,440)}</svg>'
  (OUT/f'{name}.svg').write_text(s)
 head=lambda label: text(88,97,label,19,'#d1d2d5', 'letter-spacing="4"')
 body=head('ACTIVITY / TELEMETRY')
 for x,n,label in [(160,'114','CONTRIBUTIONS'),(447,'1','CURRENT STREAK'),(720,'5','LONGEST STREAK')]:
  body+=f'<circle cx="{x}" cy="211" r="65" fill="#08090c" stroke="#43464b" stroke-width="7"/><path d="M {x-56} 240 A 64 64 0 1 1 {x+57} 240" fill="none" stroke="#d73939" stroke-width="5"/>'
  body+=text(x,228,n,48,extra='text-anchor="middle"')+text(x,317,label,16,'#b5b7bc','text-anchor="middle"')
 body+=text(88,350,'SCREENSHOT SNAPSHOT · 2026-10-06',15,'#93979e')+text(88,374,'OPEN CARD FOR LIVE CONTRIBUTION STATS ↗',15,'#e76a6a')
 panel('activity','Contribution snapshot — 2026-10-06: 114 total, 1 current streak, 5 longest streak.',body)
 langs=[('Java',53.76,'#c99350'),('TypeScript',30.41,'#5f9be4'),('Python',13.09,'#96b5c9'),('HTML',2.30,'#e36f58'),('CSS',.36,'#a58bcd'),('JavaScript',.09,'#ded599')]
 body=head('MOST USED LANGUAGES')
 x=90
 for name,value,color in langs:
  width=720*value/100
  body+=f'<rect x="{x}" y="131" width="{width}" height="12" rx="2" fill="{color}"/>'
  x+=width
 for i,(name,value,color) in enumerate(langs):
  x=90+(i//3)*370;y=200+(i%3)*58
  body+=f'<circle cx="{x}" cy="{y-7}" r="5" fill="{color}"/>'+text(x+17,y,name,22)+text(x+300,y,f'{value:.2f}%',22,'#afb5bd','text-anchor="end"')
 body+=text(90,362,'GITHUB README STATS · SNAPSHOT 2026-10-06',15,'#93979e')
 panel('languages','Most used languages — snapshot 2026-10-06',body)
 repos=[('damso','TypeScript','', '01'),('SpringAiBasic','Java','','02'),('sivertown','HTML','react vite','03'),('SpringBootMyBatis','Java','Spring Boot MyBatis project','04')]
 for repo,lang,desc,num in repos:
  body=head('FEATURED / '+num)
  body+=text(89,190,repo,35,extra='font-weight="700"')
  body+=text(90,238,desc or 'Explore source code and development history.',21,'#a8afb9')
  body+=f'<path d="M90 283H810" stroke="#46494e"/>'
  body+=f'<circle cx="98" cy="334" r="6" fill="#dc4545"/>'+text(115,342,lang,21)
  body+=text(804,342,'OPEN REPOSITORY ↗',18,'#e4e6e8','text-anchor="end"')
  panel('project-'+repo,repo+' — '+lang+' — '+desc,body)
if __name__=='__main__':build_panels()
