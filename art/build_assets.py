import bpy, math, random, os
from mathutils import Vector
random.seed(19)
OUT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../assets'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False
scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.world.color=(.22,.28,.36)
scene.view_settings.view_transform='AgX'
M={}
def mat(name,color,metal=0,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.68;p.inputs['Metallic'].default_value=metal
 if emit:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 M[name]=m;return m
for n,c in [('stone',(.23,.34,.39)),('top',(.36,.49,.47)),('edge',(.13,.22,.29)),('rock',(.12,.18,.26)),('moss',(.20,.33,.24)),('gold',(.64,.43,.17)),('cloth',(.04,.22,.25)),('dark',(.035,.07,.11)),('steel',(.57,.72,.74)),('skin',(.55,.38,.26)),('enemy',(.20,.16,.36)),('boss',(.26,.29,.35))]:mat(n,c, .65 if n in ['gold','steel'] else 0)
mat('cyan',(.13,.92,.72),.3,2.5);mat('purple',(.55,.25,.95),.3,2);mat('orange',(1,.30,.07),.3,2)
def material(o,m):o.data.materials.append(M[m]);return o
def cube(name,loc,scale,m,bev=.08):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);material(o,m)
 if bev:mod=o.modifiers.new('Soft worn edges','BEVEL');mod.width=bev;mod.segments=2;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o
def ico(name,loc,scale,m,sub=1):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;material(o,m);return o
def cone(name,loc,r1,r2,depth,m,vertices=6):
 bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r1,radius2=r2,depth=depth,location=loc);o=bpy.context.object;o.name=name;material(o,m);return o
def line(name,a,b,width,m):
 a,b=Vector(a),Vector(b);o=cube(name,(a+b)/2,(width,width,(b-a).length),m,.02);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def camera(scale,size):
 bpy.ops.object.camera_add(location=(24,-24,19.5959));cam=bpy.context.object;cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;scene.camera=cam;scene.render.resolution_x=size;scene.render.resolution_y=size;scene.render.resolution_percentage=100
 return cam
def light(name,loc,power,color,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
def setup(scale,size):
 camera(scale,size);light('Warm sun',(-8,-10,18),2200,(1,.79,.52),9);light('Moon fill',(8,4,12),1800,(.35,.66,1),10);light('Rim',(-6,8,8),1800,(.3,1,.80),8)
def render(name):
 scene.render.filepath=os.path.join(OUT,name+'.png');bpy.ops.render.render(write_still=True)
def clear():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# Floating stone foundation, top sits at z=0.
setup(33,1280)
for x in range(-8,9):
 for y in range(-8,9):
  z=-.20+random.uniform(-.025,.025);cube('Ancient paving',(x,y,z),(.97,.97,.38),random.choice(['top','top','stone']),.055)
  if abs(x)==8 or abs(y)==8:
   ico('Basalt cliff',(x,y,-1.3),(.8,.8,random.uniform(1.0,1.8)),'rock')
   if random.random()<.28:ico('Cliff moss',(x,y,.01),(.5,.5,.09),'moss')
# Copper inlays form central ritual ring.
for i in range(64):
 a=i*math.tau/64;r=3.15;o=cube('Ritual ring',(math.cos(a)*r,math.sin(a)*r,.012),(.24,.04,.018),'gold',0);o.rotation_euler.z=a+math.pi/2
for x,y in [(-7,-7),(-7,7),(7,-7),(7,7)]:
 cube('Shrine base',(x,y,.15),(1.5,1.5,.3),'stone');cube('Shrine plinth',(x,y,.55),(.95,.95,.6),'edge');cone('Crystal',(x,y,1.35),.38,0,1.4,'cyan',5)
for x,y in [(-7.5,3),(7.5,-3),(-3,7.5),(3,-7.5)]:
 cube('Broken column foot',(x,y,.18),(1.3,1.3,.36),'edge');cone('Broken column',(x,y,1.0),.46,.39,1.5,'stone',8);cube('Column cap',(x,y,1.82),(1.1,1.1,.22),'top')
for i in range(30):
 a=random.random()*math.tau;x=math.cos(a)*random.uniform(8.2,9.5);y=math.sin(a)*random.uniform(8.2,9.5)
 if abs(x)>7.8 or abs(y)>7.8:ico('Debris',(x,y,-.5),(.25,.3,.38),'rock')
# Overgrown perimeter, hanging vines, golden path fragments, and a ruined sky gate.
mat('leaf',(.11,.32,.23));mat('leafLight',(.25,.48,.29));mat('flower',(.64,.41,.65));mat('rune',(.11,.65,.49),.2,1.3)
for i in range(100):
 side=i%4;t=random.uniform(-8.2,8.2)
 x,y=[(t,-8.3),(t,8.3),(-8.3,t),(8.3,t)][side]
 for j in range(random.randint(1,3)):
  ico('Fern canopy',(x+random.uniform(-.2,.2),y+random.uniform(-.2,.2),random.uniform(.10,.28)),(random.uniform(.18,.34),.27,.19),random.choice(['leaf','leafLight']))
 if i%5==0:
  for j in range(4):ico('Hanging ivy',(x,y,-.2-j*.25),(.18,.20,.21),'leaf')
 if i%9==0:ico('Wild blossom',(x,y,.42),(.09,.09,.13),'flower')
for i in range(12):
 a=i*math.tau/12;x,y=math.cos(a)*3.15,math.sin(a)*3.15
 o=cube('Emerald glyph',(x,y,.035),(.22,.055,.025),'rune',.01);o.rotation_euler.z=a
# Arch sits outside the playable rear corner.
for t in [-.95,.95]:
 x,y=-7+t,7+t;cube('Sky gate pier',(x,y,1.55),(.65,.65,3.1),'edge');cube('Gate gilding',(x-.1,y-.1,1.7),(.07,.07,2.2),'gold',.01)
line('Broken lintel',(-8.1,5.9,3.2),(-5.9,8.1,3.2),.55,'top')
for i in range(6):
 a=i*math.tau/6;ico('Floating orbit rune',(-7+math.cos(a)*.6,7+math.cos(a)*.6,1.8+math.sin(a)*.7),(.09,.09,.14),'cyan')
render('island')
import sys
if '--island-only' in sys.argv:sys.exit(0)
clear()
# Sprite objects centered on ground origin; camera scale is shared with runtime.
def hero():
 for x in [-.18,.18]:cube('Boot',(x,-.02,.18),(.27,.43,.36),'dark');cube('Greave',(x,0,.51),(.28,.28,.37),'steel')
 cone('Coat',(0,.07,.86),.52,.31,.85,'cloth',7)
 cube('Breastplate',(0,-.12,1.17),(.62,.32,.55),'steel');cube('Belt',(0,0,.85),(.7,.44,.1),'gold')
 ico('Hood',(0,.04,1.69),(.43,.36,.46),'cloth',2);cube('Face shadow',(0,-.29,1.65),(.40,.08,.33),'dark');cube('Visor',(0,-.344,1.72),(.30,.025,.055),'cyan',.01)
 for x in [-.44,.44]:ico('Shoulder',(x,0,1.3),(.25,.28,.22),'gold');line('Arm',(x,0,1.2),(x,-.13,.87),.17,'cloth')
 line('Sword grip',(.5,-.2,.87),(.72,-.35,1.05),.1,'gold');line('Sword',(.72,-.35,1.05),(1.2,-.7,1.72),.13,'steel');line('Sword light',(.74,-.39,1.08),(1.2,-.73,1.72),.045,'cyan')
 # tapered cloak mesh
 mesh=bpy.data.meshes.new('Cape');mesh.from_pydata([(-.34,.22,1.40),(.34,.22,1.40),(.60,.62,.40),(-.60,.62,.40)],[],[(0,1,2,3)]);o=bpy.data.objects.new('Cape',mesh);bpy.context.collection.objects.link(o);material(o,'cloth');sol=o.modifiers.new('Fabric','SOLIDIFY');sol.thickness=.04

def sentinel():
 ico('Floating carapace',(0,0,1.05),(.51,.42,.58),'enemy',1)
 cone('Crown crystal',(0,0,1.67),.22,0,.65,'purple',5)
 cube('Eye',(0,-.39,1.17),(.45,.05,.07),'purple',.01)
 for x in [-.58,.58]:ico('Wing',(x,.03,.95),(.24,.22,.37),'stone');cone('Talon',(x,0,.52),.12,0,.45,'purple',4)
 cone('Floating core',(0,0,.47),0,.21,.7,'purple',5)
def guardian():
 for x in [-.42,.42]:cube('Heavy foot',(x,-.08,.24),(.68,.85,.48),'rock');cube('Leg',(x,0,.7),(.55,.6,.6),'boss')
 ico('Torso',(0,0,1.55),(.96,.62,.88),'boss',1);ico('Heart',(0,-.59,1.65),(.26,.12,.35),'orange',1)
 for x in [-1.05,1.05]:ico('Shoulder',(x,0,2.05),(.55,.6,.58),'rock');cube('Arm',(x*1.12,0,1.35),(.62,.62,.9),'boss');cube('Rune',(x*1.12,-.33,1.4),(.12,.03,.5),'orange',.01)
 cube('Head',(0,-.04,2.5),(.84,.72,.66),'rock');cube('Eyes',(0,-.41,2.55),(.56,.05,.10),'orange',.01)
 for x in [-.38,.38]:cone('Crown',(x,.1,3.03),.16,0,.6,'gold',4)
for kind,fn in [('hero',hero),('sentinel',sentinel),('guardian',guardian)]:
 clear();setup(5.8 if kind=='guardian' else 4.6,320);before=set(bpy.data.objects);fn();objects=list(set(bpy.data.objects)-before)
 for i in range(4):
  # Rotate all mesh objects together about their ground origin.
  from mathutils import Matrix
  rot=Matrix.Rotation(math.pi/2,4,'Z')
  if i:
   for o in objects:o.matrix_world=rot@o.matrix_world
  render(kind+'-'+str(i))
clear();setup(2.5,128);cone('Shard',(0,0,.5),.25,0,1,'cyan',5);cone('Shard bottom',(0,0,-.13),0,.25,.26,'cyan',5);render('shard')
print('SHARDBOUND ASSETS COMPLETE')
