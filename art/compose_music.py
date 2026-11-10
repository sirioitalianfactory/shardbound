"""Original 64-second seamless arena score, 120 BPM; requires numpy and ffmpeg."""
import numpy as np, wave, subprocess
from pathlib import Path
sr=22050;beat=.5;bars=32;length=64;n=int(sr*length);mix=np.zeros((n,2),dtype=np.float64);rng=np.random.default_rng(42)
def put(sig,start,amp=.2,pan=0):
 idx=(np.arange(len(sig))+int(start*sr))%n
 mix[idx,0]+=sig*amp*np.sqrt((1-pan)/2);mix[idx,1]+=sig*amp*np.sqrt((1+pan)/2)
def note(midi,start,dur,amp=.15,kind='lead',pan=0):
 t=np.arange(int(dur*sr))/sr;f=440*2**((midi-69)/12)
 if kind=='pad':s=np.sin(2*np.pi*f*t)+.35*np.sin(2*np.pi*f*1.003*t)+.18*np.sin(4*np.pi*f*t);env=np.minimum(t/.2,1)*np.minimum((dur-t)/.4,1)
 elif kind=='bass':s=np.sin(2*np.pi*f*t)+.3*np.sin(4*np.pi*f*t)+.12*np.sin(6*np.pi*f*t);env=np.minimum(t/.006,1)*np.exp(-t*4)*np.minimum((dur-t)/.035,1)
 else:s=sum(np.sin(2*np.pi*f*k*t+(.006*np.sin(2*np.pi*5*t)*k))*(.52**(k-1)) for k in range(1,5));env=np.minimum(t/.008,1)*np.exp(-t*2.4)*np.minimum((dur-t)/.045,1)
 put(s*env,start,amp,pan)
def drum(start,kind,amp=1):
 dur={'kick':.32,'snare':.19,'hat':.055,'open':.22}[kind];t=np.arange(int(dur*sr))/sr
 if kind=='kick':s=np.sin(2*np.pi*(42*t+65*.035*(1-np.exp(-t/.035))))*np.exp(-t*15)
 else:
  noise=rng.normal(0,.4,len(t));noise=np.r_[0,np.diff(noise)]
  s=(noise*.5+np.sin(2*np.pi*180*t)*.22)*np.exp(-t*23) if kind=='snare' else noise*np.exp(-t*(70 if kind=='hat' else 18))*.28
 put(s,start,amp, .25 if kind in ['hat','open'] else 0)
# Em — C — G — D: four distinct eight-bar sections with a quieter middle break.
chords=[(40,[64,67,71]),(36,[60,64,67]),(43,[62,67,71]),(38,[62,66,69])]
motif=[[76,79,83,81,79,76,74,71],[76,79,84,83,79,76,79,74],[79,83,86,83,81,79,74,76],[78,81,86,84,81,78,74,71]]
for bar in range(bars):
 start=bar*2;root,chord=chords[bar%4];section=bar//8;breakdown=section==2 and bar%8<4
 for j,m in enumerate(chord):note(m-12,start,2.25,.052,'pad',[-.65,0,.65][j])
 for k in range(8):
  note(root+(12 if k in [3,6] else 0),start+k*.25,.20,.21 if not breakdown else .11,'bass')
  if not breakdown:note(chord[k%3]+12,start+k*.25,.20,.045,'lead',(-.45 if k%2 else .45))
 if section!=0 or bar>=4:
  for k,m in enumerate(motif[bar%4]):
   at=start+k*.25;note(m+(12 if section==3 and k==6 else 0),at,.24 if k<7 else .4,.11 if not breakdown else .07,'lead',.06)
 if not breakdown:
  for b in range(4):drum(start+b*.5,'kick',.58);drum(start+b*.5+.25,'hat',.34)
  for b in [1,3]:drum(start+b*.5,'snare',.66)
  if bar%4==3:
   for k in range(4):drum(start+1.5+k*.125,'snare',.18+k*.035)
  if section in [1,3]:drum(start+1.75,'open',.27)
# Stereo ping-pong echoes and a short room tail, wrapped for a seamless loop.
dry=mix.copy()
for delay,gain in [(.375,.19),(.75,.09),(.07,.07)]:mix+=np.roll(dry[:,::-1],int(delay*sr),axis=0)*gain
mix=np.tanh(mix*1.2);mix*=.88/max(.88,np.max(np.abs(mix)))
out=Path(__file__).resolve().parent.parent/'assets'/'shardbound-theme.mp3';tmp=out.with_suffix('.wav')
with wave.open(str(tmp),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((mix*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(tmp),'-codec:a','libmp3lame','-b:a','80k',str(out)],check=True);tmp.unlink();print(out.stat().st_size)
