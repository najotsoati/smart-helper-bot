# video_namuna.py  -  namuna animatsiya (12 soniya = 360 kadr)
# Ishga tushirish: tepadagi "Scripting" bo'limi -> shu faylni tanlang -> uchburchak (Run Script) tugmasi
import bpy
st = bpy.data.texts["stickman_tools.py"].as_module()

st.clear_animation()
bpy.context.scene.frame_end = 360        # 30 kadr = 1 soniya

st.hold("stand", 1, 14)                  # tinch turadi
st.apply_pose("wave", 26)                # salom beradi
st.apply_pose("wave2", 34)
st.apply_pose("wave", 42)
st.apply_pose("wave2", 50)
st.apply_pose("wave", 58)
st.blink(46)
st.hold("stand", 76, 92)

st.hold("think", 110, 188)               # o'ylaydi
st.prop("question", 116, 184)            # ??? chiqadi
st.look(0.0, 0.0, 108)
st.look(0.03, 0.03, 120)
st.look(0.03, 0.03, 180)
st.look(0.0, 0.0, 192)
st.blink(150)

st.hold("idea", 204, 262)                # g'oya keldi!
st.prop("bulb", 204, 258)                # lampochka
st.hop(204, height=0.3, length=10)

st.hold("present", 280, 330)             # tushuntiradi
st.talk(282, 328)                        # gapiradi
st.blink(300)
st.hold("hips", 346, 360)

bpy.context.scene.frame_set(1)
