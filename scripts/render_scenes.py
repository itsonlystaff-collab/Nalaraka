import os
import sys
import math
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene_builder import (
    clear_scene, get_or_create_material, create_box, create_cylinder,
    create_icosphere, create_lowpoly_character, set_facial_expression,
    animate_walk_cycle, create_lowpoly_tree, create_mrt_train,
    create_transjakarta_bus, create_private_car, create_monas_landmark,
    setup_lighting_and_world
)

FPS = 30
RES_X = 1080
RES_Y = 1920

# Total durasi 75 detik = 2250 frame (VO = 72.12s + 1.0s intro + 1.88s outro)
SCENES_TIMELINE = [
    ("scene_01", 0, 240),     # 00:00 - 00:08 (8s): Meninggalkan mobil pribadi di rumah
    ("scene_02", 240, 480),   # 00:08 - 00:16 (8s): MRT, KRL, dan TransJakarta
    ("scene_03", 480, 750),   # 00:16 - 00:25 (9s): Pekerja & pelajar di dalam gerbong
    ("scene_04", 750, 990),   # 00:25 - 00:33 (8s): Lalu lintas Jakarta tertib, macet berkurang
    ("scene_05", 990, 1260),  # 00:33 - 00:42 (9s): Polusi menurun, hemat biaya, ekspresi lega
    ("scene_06", 1260, 1440), # 00:42 - 00:48 (6s): Waktu produktif membaca/kerja di taman
    ("scene_07", 1440, 1680), # 00:48 - 00:56 (8s): Parkir berubah jadi taman, trotoar & jalur sepeda
    ("scene_08", 1680, 1860), # 00:56 - 01:02 (6s): Udara segar, kota sehat & ramah lingkungan
    ("scene_09", 1860, 2070), # 01:02 - 01:09 (7s): Menikmati perjalanan berlatar Monas
    ("scene_10", 2070, 2250), # 01:09 - 01:15 (6s): Penutup keputusan sederhana memilih transportasi umum
]

def configure_render(output_filepath, frame_start, frame_end):
    scene = bpy.context.scene
    engine = os.environ.get("RENDER_ENGINE", "BLENDER_EEVEE_NEXT")
    samples = int(os.environ.get("RENDER_SAMPLES", "8"))

    scene.render.engine = engine

    if engine == "BLENDER_EEVEE_NEXT":
        scene.eevee.taa_render_samples = samples
    elif engine == "CYCLES":
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True

    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.render.fps_base = 1.0

    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.ffmpeg.gopsize = 15
    scene.render.ffmpeg.audio_codec = 'NONE'

    scene.render.filepath = output_filepath
    scene.frame_start = frame_start
    scene.frame_end = frame_end

def create_camera(name="MainCam", location=(0, -6, 2.2), rotation=(math.radians(78), 0, 0), lens=35.0):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = location
    cam_obj.rotation_euler = rotation
    bpy.context.scene.camera = cam_obj
    return cam_obj

def build_ground_and_buildings(clean_air=True):
    mat_asphalt = get_or_create_material("Asphalt", (0.16, 0.17, 0.19), roughness=0.85)
    mat_sidewalk = get_or_create_material("Sidewalk", (0.72, 0.73, 0.75), roughness=0.75)
    mat_grass = get_or_create_material("Grass", (0.20, 0.62, 0.26), roughness=0.8)

    create_box("RoadPlane", size=(14, 120, 0.2), location=(0, 20, -0.1), mat=mat_asphalt, bevel_width=0.0)
    create_box("SidewalkL", size=(5, 120, 0.32), location=(-9.5, 20, 0.0), mat=mat_sidewalk, bevel_width=0.02)
    create_box("SidewalkR", size=(5, 120, 0.32), location=(9.5, 20, 0.0), mat=mat_sidewalk, bevel_width=0.02)
    create_box("ParkStrip", size=(20, 120, 0.15), location=(-22, 20, -0.05), mat=mat_grass, bevel_width=0.0)

    b_colors = [(0.78, 0.82, 0.88), (0.68, 0.74, 0.82), (0.85, 0.84, 0.80), (0.58, 0.66, 0.76)]
    for i in range(8):
        y_pos = -10 + i * 14
        h1 = 10 + (i % 4) * 5
        h2 = 12 + ((i + 2) % 4) * 6
        mat_b1 = get_or_create_material(f"BldgMat_{i%4}", b_colors[i % 4], roughness=0.6)
        create_box(f"BldgL_{i}", size=(8, 9, h1), location=(-17, y_pos, h1 / 2), mat=mat_b1, bevel_width=0.1)
        create_box(f"BldgR_{i}", size=(8, 9, h2), location=(17, y_pos, h2 / 2), mat=mat_b1, bevel_width=0.1)

def build_scene_01(f_start, f_end):
    clear_scene()
    setup_lighting_and_world(sky_color=(0.95, 0.76, 0.55), sun_energy=4.0)
    build_ground_and_buildings()
    create_lowpoly_tree("TreeHome1", location=(-7.8, 3, 0.15), scale=1.1)

    car, _ = create_private_car("HomeCar", location=(-4.2, -1.5, 0), color=(0.82, 0.24, 0.22))
    car.rotation_euler.z = math.radians(15)

    hero = create_lowpoly_character("Andra", location=(-6.2, -1.5, 0.16), rotation=(0, 0, math.radians(-90)))
    animate_walk_cycle(hero, f_start, f_end, speed=1.0)

    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)
        hero["root"].location = (-6.2 - p * 2.5, -1.5 + p * 6.5, 0.16)
        hero["root"].rotation_euler.z = math.radians(-160)
        hero["root"].keyframe_insert(data_path="location", frame=f)
        hero["root"].keyframe_insert(data_path="rotation_euler", frame=f)
        set_facial_expression(hero, f, mood="smile", talk_phase=p * 12)

    cam = create_camera("Cam01", location=(-4.0, -7.5, 2.3), rotation=(math.radians(80), 0, math.radians(15)), lens=32)
    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)
        cam.location = (-4.0 - p * 1.8, -7.5 + p * 4.5, 2.1)
        cam.keyframe_insert(data_path="location", frame=f)

def build_scene_02(f_start, f_end):
    clear_scene()
    setup_lighting_and_world(sky_color=(0.45, 0.75, 0.98), sun_energy=4.2)
    build_ground_and_buildings()

    # Jalur Layang MRT
    mat_concrete = get_or_create_material("ViaductMat", (0.76, 0.77, 0.79), roughness=0.7)
    create_box("MRT_Track", size=(3.4, 120, 0.8), location=(-3.5, 20, 6.5), mat=mat_concrete, bevel_width=0.05)
    for py in range(-10, 60, 12):
        create_box(f"MRT_Pillar_{py}", size=(1.4, 1.4, 6.5), location=(-3.5, py, 3.25), mat=mat_concrete, bevel_width=0.05)

    mrt = create_mrt_train("MRT_01", location=(-3.5, -25, 6.9))
    tj, tj_wheels = create_transjakarta_bus("TJ_01", location=(3.2, -18, 0))
    c1 = create_lowpoly_character("Commuter1", location=(7.8, 2.0, 0.16), rotation=(0, 0, math.radians(-90)))

    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)
        mrt.location.y = -25 + p * 55.0
        mrt.keyframe_insert(data_path="location", frame=f)

        tj.location.y = -18 + p * 22.0
        tj.keyframe_insert(data_path="location", frame=f)
        for w in tj_wheels:
            w.rotation_euler.x = -p * 28.0
            w.keyframe_insert(data_path="rotation_euler", frame=f)

        set_facial_expression(c1, f, mood="happy_wide", talk_phase=p * 10)

    cam = create_camera("Cam02", location=(6.5, -9.5, 2.0), rotation=(math.radians(96), 0, math.radians(28)), lens=28)
    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)
        cam.location = (6.5, -9.5 + p * 3.0, 2.0 + p * 0.8)
        cam.keyframe_insert(data_path="location", frame=f)

def build_scene_03(f_start, f_end):
    clear_scene()
    setup_lighting_and_world(sky_color=(0.55, 0.80, 0.98), sun_energy=3.5)

    # Interior Gerbong MRT Low-Poly
    mat_wall = get_or_create_material("CabinWall", (0.92, 0.94, 0.96), roughness=0.4)
    mat_floor = get_or_create_material("CabinFloor", (0.35, 0.40, 0.48), roughness=0.6)
    mat_seat = get_or_create_material("CabinSeat", (0.12, 0.46, 0.84), roughness=0.5)

    create_box("Cabin_Floor", size=(2.6, 10.0, 0.2), location=(0, 0, -0.1), mat=mat_floor)
    create_box("Cabin_WallL", size=(0.15, 10.0, 2.5), location=(-1.3, 0, 1.25), mat=mat_wall)
    create_box("Cabin_Roof", size=(2.7, 10.0, 0.2), location=(0, 0, 2.5), mat=mat_wall)
    create_box("Cabin_BenchL", size=(0.55, 8.0, 0.45), location=(-0.95, 0, 0.22), mat=mat_seat, bevel_width=0.04)

    # Pekerja & Pelajar di dalam kereta
    worker = create_lowpoly_character("Worker", location=(-0.85, 0.4, 0.15), rotation=(0, 0, math.radians(-85)), shirt_color=(0.2, 0.5, 0.8))
    student = create_lowpoly_character("Student", location=(-0.85, 1.5, 0.15), rotation=(0, 0, math.radians(-95)), is_student=True)

    # Posisi duduk (tekuk kaki)
    for ch in (worker, student):
        ch["torso"].location.z = 0.82
        ch["leg_l"].rotation_euler.x = math.radians(-85)
        ch["leg_r"].rotation_euler.x = math.radians(-85)

    # Gedung luar bergerak memberi efek kereta melaju
    bldg_out = create_box("PassBldg", size=(6, 8, 22), location=(-8, -15, 5), mat=get_or_create_material("OutBldg", (0.7, 0.78, 0.88)))

    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)
        bldg_out.location.y = -20 + ((p * 80) % 45)
        bldg_out.keyframe_insert(data_path="location", frame=f)

        worker["head_pivot"].rotation_euler.z = math.sin(p * 6.0) * math.radians(12)
        student["head_pivot"].rotation_euler.z = -math.sin(p * 6.0) * math.radians(10)
        worker["head_pivot"].keyframe_insert(data_path="rotation_euler", frame=f)
        student["head_pivot"].keyframe_insert(data_path="rotation_euler", frame=f)

        set_facial_expression(worker, f, mood="smile", talk_phase=p * 14)
        set_facial_expression(student, f, mood="happy_wide", talk_phase=p * 10)

    cam = create_camera("Cam03", location=(0.65, -1.6, 1.35), rotation=(math.radians(86), 0, math.radians(22)), lens=35)
    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)
        cam.location = (0.65, -1.6 + p * 0.8, 1.35)
        cam.keyframe_insert(data_path="location", frame=f)

def build_scene_04(f_start, f_end):
    clear_scene()
    setup_lighting_and_world(sky_color=(0.45, 0.75, 0.98), sun_energy=4.2)
    build_ground_and_buildings()

    bus1, w1 = create_transjakarta_bus("Bus_North", location=(2.8, -15, 0))
    bus2, w2 = create_transjakarta_bus("Bus_South", location=(-2.8, 25, 0))
    bus2.rotation_euler.z = math.radians(180)
    car1, cw1 = create_private_car("TidyCar", location=(0.2, -22, 0), color=(0.25, 0.62, 0.78))

    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)
        bus1.location.y = -15 + p * 35
        bus2.location.y = 25 - p * 35
        car1.location.y = -22 + p * 38
        for obj in (bus1, bus2, car1):
            obj.keyframe_insert(data_path="location", frame=f)
        for w in w1 + w2 + cw1:
            w.rotation_euler.x = -p * 30
            w.keyframe_insert(data_path="rotation_euler", frame=f)

    cam = create_camera("Cam04", location=(0, -14, 14), rotation=(math.radians(48), 0, 0), lens=30)
    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)
        cam.location = (p * 2.5, -14 + p * 4.0, 14 - p * 2.0)
        cam.keyframe_insert(data_path="location", frame=f)

def build_scene_05(f_start, f_end):
    clear_scene()
    world, sun = setup_lighting_and_world(sky_color=(0.62, 0.64, 0.66), sun_energy=2.2)
    build_ground_and_buildings()
    create_lowpoly_tree("Tree05", location=(-8.5, 4, 0.15), scale=1.2)

    hero = create_lowpoly_character("Andra05", location=(-7.8, 0, 0.16), rotation=(0, 0, math.radians(-20)))
    # Mengangkat tangan kanan memegang kartu/ponsel hemat
    hero["arm_r"].rotation_euler.x = math.radians(-55)
    card = create_box("SavingsCard", size=(0.14, 0.02, 0.22), location=(0, -0.05, -0.34),
                      mat=get_or_create_material("CardGold", (0.15, 0.78, 0.45), emission_strength=0.4), parent=hero["arm_r"])

    bg = world.node_tree.nodes.get("Background")
    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)
        # Transisi langit dari polusi kelabu ke biru jernih segar
        if bg:
            r = 0.62 * (1 - p) + 0.42 * p
            g = 0.64 * (1 - p) + 0.76 * p
            b = 0.66 * (1 - p) + 0.98 * p
            bg.inputs["Color"].default_value = (r, g, b, 1.0)
            bg.inputs["Color"].keyframe_insert(data_path="default_value", frame=f)
        sun.data.energy = 2.2 + p * 2.2
        sun.data.keyframe_insert(data_path="energy", frame=f)
        set_facial_expression(hero, f, mood="happy_wide" if p > 0.4 else "smile", talk_phase=p * 10)

    cam = create_camera("Cam05", location=(-7.3, -2.2, 1.55), rotation=(math.radians(88), 0, math.radians(-12)), lens=42)
    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)
        cam.location = (-7.3, -2.2 + p * 0.45, 1.55)
        cam.keyframe_insert(data_path="location", frame=f)

def build_scene_06(f_start, f_end):
    clear_scene()
    setup_lighting_and_world(sky_color=(0.45, 0.78, 0.98), sun_energy=4.0)
    build_ground_and_buildings()

    mat_wood = get_or_create_material("BenchWood", (0.58, 0.34, 0.16), roughness=0.7)
    create_box("ParkBench", size=(1.8, 0.65, 0.45), location=(-12.5, 2.0, 0.22), mat=mat_wood, bevel_width=0.03)
    create_lowpoly_tree("ParkTree06", location=(-14.2, 3.8, 0.0), scale=1.4)

    reader = create_lowpoly_character("Reader", location=(-12.5, 2.0, 0.15), rotation=(0, 0, math.radians(-35)))
    reader["torso"].location.z = 0.82
    reader["leg_l"].rotation_euler.x = math.radians(-85)
    reader["leg_r"].rotation_euler.x = math.radians(-85)
    reader["arm_l"].rotation_euler.x = math.radians(-48)
    reader["arm_r"].rotation_euler.x = math.radians(-48)

    book = create_box("BookObj", size=(0.32, 0.24, 0.04), location=(0, -0.28, -0.25),
                      mat=get_or_create_material("BookCover", (0.95, 0.65, 0.15)), parent=reader["torso"])

    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)
        set_facial_expression(reader, f, mood="happy_wide", talk_phase=p * 8)

    cam = create_camera("Cam06", location=(-10.5, -0.6, 1.5), rotation=(math.radians(84), 0, math.radians(35)), lens=38)
    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)
        cam.location = (-10.5 - p * 1.4, -0.6 - p * 0.4, 1.55)
        cam.rotation_euler.z = math.radians(35 - p * 28)
        cam.keyframe_insert(data_path="location", frame=f)
        cam.keyframe_insert(data_path="rotation_euler", frame=f)

def build_scene_07(f_start, f_end):
    clear_scene()
    setup_lighting_and_world(sky_color=(0.45, 0.78, 0.98), sun_energy=4.2)
    build_ground_and_buildings()

    # Lahan parkir berubah menjadi taman hijau + jalur sepeda hijau
    mat_park_grass = get_or_create_material("NewParkGrass", (0.22, 0.72, 0.28), roughness=0.75)
    mat_bike_lane = get_or_create_material("BikeLaneGreen", (0.12, 0.65, 0.35), roughness=0.6)

    park_pad = create_box("TransformedPark", size=(6.5, 16.0, 0.28), location=(-12.5, 4.0, 0.14), mat=mat_park_grass, bevel_width=0.04)
    create_box("BikeLane", size=(1.6, 60.0, 0.34), location=(-7.6, 15.0, 0.01), mat=mat_bike_lane)

    t1, c1a, c1b = create_lowpoly_tree("GrowTree1", location=(-13.5, 2.0, 0.28), scale=1.2)
    t2, c2a, c2b = create_lowpoly_tree("GrowTree2", location=(-11.5, 7.5, 0.28), scale=1.35)

    cyclist = create_lowpoly_character("Cyclist", location=(-7.6, -6.0, 0.45), rotation=(0, 0, math.radians(180)), shirt_color=(0.95, 0.45, 0.15))
    bike_frame = create_box("BikeFrame", size=(0.14, 1.4, 0.55), location=(0, 0, 0.42),
                            mat=get_or_create_material("BikeMetal", (0.95, 0.80, 0.12), metallic=0.6), parent=cyclist["root"])

    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)
        grow = min(1.0, p * 1.6)
        t1.scale = (grow * 1.2, grow * 1.2, grow * 1.2)
        t2.scale = (grow * 1.35, grow * 1.35, grow * 1.35)
        t1.keyframe_insert(data_path="scale", frame=f)
        t2.keyframe_insert(data_path="scale", frame=f)

        cyclist["root"].location.y = -6.0 + p * 18.0
        cyclist["root"].keyframe_insert(data_path="location", frame=f)
        set_facial_expression(cyclist, f, mood="happy_wide", talk_phase=p * 8)

    cam = create_camera("Cam07", location=(-5.0, -7.5, 3.2), rotation=(math.radians(72), 0, math.radians(26)), lens=30)
    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)
        cam.location = (-5.0 + p * 2.0, -7.5 - p * 2.5, 3.2 + p * 1.5)
        cam.keyframe_insert(data_path="location", frame=f)

def build_scene_08(f_start, f_end):
    clear_scene()
    setup_lighting_and_world(sky_color=(0.40, 0.78, 0.99), sun_energy=4.4)
    build_ground_and_buildings()
    create_lowpoly_tree("FreshTree1", location=(-8.8, 2.5, 0.16), scale=1.3)
    create_lowpoly_tree("FreshTree2", location=(-10.5, 5.5, 0.16), scale=1.5)

    hero = create_lowpoly_character("Andra08", location=(-7.6, 0.0, 0.16), rotation=(0, 0, math.radians(-15)))
    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)
        # Animasi menarik napas dalam (dada mengembang halus & kepala sedikit menengadah)
        breath = math.sin(p * math.pi)
        hero["torso"].scale = (1.0 + breath * 0.06, 1.0 + breath * 0.08, 1.0 + breath * 0.04)
        hero["head_pivot"].rotation_euler.x = breath * math.radians(10)
        hero["torso"].keyframe_insert(data_path="scale", frame=f)
        hero["head_pivot"].keyframe_insert(data_path="rotation_euler", frame=f)
        set_facial_expression(hero, f, mood="calm_inhale" if p < 0.65 else "happy_wide", talk_phase=0.0)

    cam = create_camera("Cam08", location=(-7.2, -1.75, 1.62), rotation=(math.radians(89), 0, math.radians(-10)), lens=48)
    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)
        cam.location = (-7.2, -1.75 - p * 0.35, 1.62)
        cam.keyframe_insert(data_path="location", frame=f)

def build_scene_09(f_start, f_end):
    clear_scene()
    setup_lighting_and_world(sky_color=(0.42, 0.77, 0.99), sun_energy=4.3)
    build_ground_and_buildings()
    create_monas_landmark(location=(0, 42, 0))
    create_lowpoly_tree("Tree09A", location=(-8.8, 5, 0.16), scale=1.2)
    create_lowpoly_tree("Tree09B", location=(8.8, 10, 0.16), scale=1.3)

    hero = create_lowpoly_character("Andra09", location=(-7.5, -2.0, 0.16), rotation=(0, 0, math.radians(165)))
    animate_walk_cycle(hero, f_start, f_end, speed=0.9)

    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)
        hero["root"].location.y = -2.0 + p * 7.5
        hero["root"].keyframe_insert(data_path="location", frame=f)
        # Melambaikan tangan ramah
        hero["arm_r"].rotation_euler.y = math.radians(-135) + math.sin(p * 14) * math.radians(18)
        hero["arm_r"].keyframe_insert(data_path="rotation_euler", frame=f)
        set_facial_expression(hero, f, mood="happy_wide", talk_phase=p * 10)

    cam = create_camera("Cam09", location=(-5.8, -5.5, 2.0), rotation=(math.radians(85), 0, math.radians(16)), lens=32)
    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)
        cam.location = (-5.8 + p * 2.5, -5.5 + p * 7.0, 2.0 + p * 0.6)
        cam.keyframe_insert(data_path="location", frame=f)

def build_scene_10(f_start, f_end):
    clear_scene()
    setup_lighting_and_world(sky_color=(0.42, 0.78, 0.99), sun_energy=4.4)
    build_ground_and_buildings()
    create_monas_landmark(location=(0, 44, 0))

    mrt = create_mrt_train("MRT_Finale", location=(0, 14, 0.2))
    mrt.rotation_euler.z = math.radians(90)

    citizens = [
        create_lowpoly_character("CitA", location=(-7.5, -3.0, 0.16), rotation=(0, 0, math.radians(175)), shirt_color=(0.15, 0.55, 0.88)),
        create_lowpoly_character("CitB", location=(-8.5, -1.5, 0.16), rotation=(0, 0, math.radians(175)), is_student=True),
        create_lowpoly_character("CitC", location=(7.5, -2.5, 0.16), rotation=(0, 0, math.radians(-175)), shirt_color=(0.92, 0.42, 0.22)),
    ]
    for c in citizens:
        animate_walk_cycle(c, f_start, f_end, speed=0.95)

    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)
        for idx, c in enumerate(citizens):
            c["root"].location.y = -3.0 + idx * 0.6 + p * 6.5
            c["root"].keyframe_insert(data_path="location", frame=f)
            set_facial_expression(c, f, mood="happy_wide", talk_phase=p * 8)

    cam = create_camera("Cam10", location=(0, -8.5, 2.6), rotation=(math.radians(82), 0, 0), lens=28)
    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)
        cam.location = (0, -8.5 - p * 4.5, 2.6 + p * 6.5)
        cam.rotation_euler.x = math.radians(82 - p * 14)
        cam.keyframe_insert(data_path="location", frame=f)
        cam.keyframe_insert(data_path="rotation_euler", frame=f)

BUILDERS = {
    "scene_01": build_scene_01,
    "scene_02": build_scene_02,
    "scene_03": build_scene_03,
    "scene_04": build_scene_04,
    "scene_05": build_scene_05,
    "scene_06": build_scene_06,
    "scene_07": build_scene_07,
    "scene_08": build_scene_08,
    "scene_09": build_scene_09,
    "scene_10": build_scene_10,
}

def main():
    os.makedirs("renders/scenes", exist_ok=True)

    # ==========================================
    # SCENE FILTER FOR GITHUB ACTIONS
    # ==========================================

    scene_filter = {
        item.strip()
        for item in os.environ.get("SCENE_FILTER", "").split(",")
        if item.strip()
    }

   if not scene_filter:
    raise RuntimeError(
        "SCENE_FILTER kosong! "
        "Render dibatalkan untuk mencegah render semua scene berulang."
    )

    valid_scenes = {
        scene_id for scene_id, _, _ in SCENES_TIMELINE
    }

    invalid_scenes = scene_filter - valid_scenes

    if invalid_scenes:
        raise ValueError(
            f"Scene tidak dikenal: {sorted(invalid_scenes)}"
        )

   selected_scenes = [
    item
    for item in SCENES_TIMELINE
    if item[0] in scene_filter   
    ]

    if not selected_scenes:
        raise RuntimeError("Tidak ada scene yang dipilih!")

    render_engine = os.environ.get(
        "RENDER_ENGINE",
        "BLENDER_EEVEE_NEXT"
    )

    render_samples = os.environ.get(
        "RENDER_SAMPLES",
        "8"
    )

    print("\n" + "=" * 60)
    print("JAKARTA LOW-POLY 3D RENDER")
    print("=" * 60)
    print(f"Render Engine : {render_engine}")
    print(f"Samples       : {render_samples}")
    print(f"Total Scenes  : {len(selected_scenes)}")
    print(
        "Scene List   :",
        [scene[0] for scene in selected_scenes]
    )
    print("=" * 60 + "\n", flush=True)

    # ==========================================
    # RENDER SELECTED SCENES
    # ==========================================

    for index, (scene_id, f_start, f_end) in enumerate(
        selected_scenes,
        start=1
    ):

        print("\n" + "-" * 60, flush=True)
        print(
            f"[{index}/{len(selected_scenes)}] "
            f"BUILDING {scene_id}",
            flush=True
        )
        print(
            f"Frames: {f_start} - {f_end - 1}",
            flush=True
        )
        print("-" * 60, flush=True)

        # Build scene
        if scene_id not in BUILDERS:
            raise RuntimeError(
                f"Builder tidak ditemukan: {scene_id}"
            )

        BUILDERS[scene_id](f_start, f_end - 1)

        # Output MP4
        out_mp4 = os.path.abspath(
            f"renders/scenes/{scene_id}.mp4"
        )

        # Configure render
        configure_render(
            out_mp4,
            f_start,
            f_end - 1
        )

        # Render animation
        print(
            f"START RENDER: {scene_id}",
            flush=True
        )

        bpy.ops.render.render(animation=True)

        # Verify output
        if not os.path.isfile(out_mp4):
            raise RuntimeError(
                f"File hasil render tidak ditemukan: {out_mp4}"
            )

        if os.path.getsize(out_mp4) == 0:
            raise RuntimeError(
                f"File hasil render kosong: {out_mp4}"
            )

        print(
            f"SUCCESS: {scene_id} selesai!",
            flush=True
        )
        print(
            f"Output: {out_mp4}",
            flush=True
        )

    print("\n" + "=" * 60)
    print("SEMUA SCENE DALAM KELOMPOK BERHASIL DIRENDER!")
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
