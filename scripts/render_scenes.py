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

# Total durasi 75 detik = 2250 frame
SCENES_TIMELINE = [
    ("scene_01", 0, 240),
    ("scene_02", 240, 480),
    ("scene_03", 480, 750),
    ("scene_04", 750, 990),
    ("scene_05", 990, 1260),
    ("scene_06", 1260, 1440),
    ("scene_07", 1440, 1680),
    ("scene_08", 1680, 1860),
    ("scene_09", 1860, 2070),
    ("scene_10", 2070, 2250),
]


def configure_render(output_filepath, frame_start, frame_end):
    scene = bpy.context.scene

    engine = os.environ.get(
        "RENDER_ENGINE",
        "BLENDER_EEVEE_NEXT"
    )

    samples = max(
        4,
        int(os.environ.get("RENDER_SAMPLES", "4"))
    )

    scene.render.engine = engine

    if engine == "BLENDER_EEVEE_NEXT":
        eevee_settings = getattr(scene, "eevee", None)

        if (
            eevee_settings is None
            or not hasattr(eevee_settings, "taa_render_samples")
        ):
            raise RuntimeError(
                "Pengaturan Eevee render samples tidak tersedia "
                "pada versi Blender ini."
            )

        eevee_settings.taa_render_samples = samples

    elif engine == "CYCLES":
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True

    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.resolution_percentage = 100

    scene.render.fps = FPS
    scene.render.fps_base = 1.0

    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.ffmpeg.gopsize = 15
    scene.render.ffmpeg.audio_codec = "NONE"

    scene.render.filepath = output_filepath
    scene.frame_start = frame_start
    scene.frame_end = frame_end

    scene.render.use_file_extension = True
    scene.render.use_overwrite = True

    print(f"ENGINE: {engine}", flush=True)
    print(f"SAMPLES: {samples}", flush=True)
    print(f"OUTPUT: {output_filepath}", flush=True)


def create_camera(
    name="MainCam",
    location=(0, -6, 2.2),
    rotation=(math.radians(78), 0, 0),
    lens=35.0
):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens

    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_obj)

    cam_obj.location = location
    cam_obj.rotation_euler = rotation

    bpy.context.scene.camera = cam_obj

    return cam_obj


def build_ground_and_buildings(clean_air=True):
    mat_asphalt = get_or_create_material(
        "Asphalt",
        (0.16, 0.17, 0.19),
        roughness=0.85
    )

    mat_sidewalk = get_or_create_material(
        "Sidewalk",
        (0.72, 0.73, 0.75),
        roughness=0.75
    )

    mat_grass = get_or_create_material(
        "Grass",
        (0.20, 0.62, 0.26),
        roughness=0.8
    )

    create_box(
        "RoadPlane",
        size=(14, 120, 0.2),
        location=(0, 20, -0.1),
        mat=mat_asphalt,
        bevel_width=0.0
    )

    create_box(
        "SidewalkL",
        size=(5, 120, 0.32),
        location=(-9.5, 20, 0.0),
        mat=mat_sidewalk,
        bevel_width=0.02
    )

    create_box(
        "SidewalkR",
        size=(5, 120, 0.32),
        location=(9.5, 20, 0.0),
        mat=mat_sidewalk,
        bevel_width=0.02
    )

    create_box(
        "ParkStrip",
        size=(20, 120, 0.15),
        location=(-22, 20, -0.05),
        mat=mat_grass,
        bevel_width=0.0
    )

    b_colors = [
        (0.78, 0.82, 0.88),
        (0.68, 0.74, 0.82),
        (0.85, 0.84, 0.80),
        (0.58, 0.66, 0.76)
    ]

    for i in range(8):
        y_pos = -10 + i * 14

        h1 = 10 + (i % 4) * 5
        h2 = 12 + ((i + 2) % 4) * 6

        mat_b1 = get_or_create_material(
            f"BldgMat_{i%4}",
            b_colors[i % 4],
            roughness=0.6
        )

        create_box(
            f"BldgL_{i}",
            size=(8, 9, h1),
            location=(-17, y_pos, h1 / 2),
            mat=mat_b1,
            bevel_width=0.1
        )

        create_box(
            f"BldgR_{i}",
            size=(8, 9, h2),
            location=(17, y_pos, h2 / 2),
            mat=mat_b1,
            bevel_width=0.1
        )


def build_scene_01(f_start, f_end):
    clear_scene()

    setup_lighting_and_world(
        sky_color=(0.95, 0.76, 0.55),
        sun_energy=4.0
    )

    build_ground_and_buildings()

    create_lowpoly_tree(
        "TreeHome1",
        location=(-7.8, 3, 0.15),
        scale=1.1
    )

    car, _ = create_private_car(
        "HomeCar",
        location=(-4.2, -1.5, 0),
        color=(0.82, 0.24, 0.22)
    )

    car.rotation_euler.z = math.radians(15)

    hero = create_lowpoly_character(
        "Andra",
        location=(-6.2, -1.5, 0.16),
        rotation=(0, 0, math.radians(-90))
    )

    animate_walk_cycle(
        hero,
        f_start,
        f_end,
        speed=1.0
    )

    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)

        hero["root"].location = (
            -6.2 - p * 2.5,
            -1.5 + p * 6.5,
            0.16
        )

        hero["root"].rotation_euler.z = math.radians(-160)

        hero["root"].keyframe_insert(
            data_path="location",
            frame=f
        )

        hero["root"].keyframe_insert(
            data_path="rotation_euler",
            frame=f
        )

        set_facial_expression(
            hero,
            f,
            mood="smile",
            talk_phase=p * 12
        )

    cam = create_camera(
        "Cam01",
        location=(-4.0, -7.5, 2.3),
        rotation=(
            math.radians(80),
            0,
            math.radians(15)
        ),
        lens=32
    )

    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)

        cam.location = (
            -4.0 - p * 1.8,
            -7.5 + p * 4.5,
            2.1
        )

        cam.keyframe_insert(
            data_path="location",
            frame=f
        )


def build_scene_02(f_start, f_end):
    clear_scene()

    setup_lighting_and_world(
        sky_color=(0.45, 0.75, 0.98),
        sun_energy=4.2
    )

    build_ground_and_buildings()

    mat_concrete = get_or_create_material(
        "ViaductMat",
        (0.76, 0.77, 0.79),
        roughness=0.7
    )

    create_box(
        "MRT_Track",
        size=(3.4, 120, 0.8),
        location=(-3.5, 20, 6.5),
        mat=mat_concrete,
        bevel_width=0.05
    )

    for py in range(-10, 60, 12):
        create_box(
            f"MRT_Pillar_{py}",
            size=(1.4, 1.4, 6.5),
            location=(-3.5, py, 3.25),
            mat=mat_concrete,
            bevel_width=0.05
        )

    mrt = create_mrt_train(
        "MRT_01",
        location=(-3.5, -25, 6.9)
    )

    tj, tj_wheels = create_transjakarta_bus(
        "TJ_01",
        location=(3.2, -18, 0)
    )

    c1 = create_lowpoly_character(
        "Commuter1",
        location=(7.8, 2.0, 0.16),
        rotation=(0, 0, math.radians(-90))
    )

    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)

        mrt.location.y = -25 + p * 55.0
        mrt.keyframe_insert(
            data_path="location",
            frame=f
        )

        tj.location.y = -18 + p * 22.0
        tj.keyframe_insert(
            data_path="location",
            frame=f
        )

        for w in tj_wheels:
            w.rotation_euler.x = -p * 28.0

            w.keyframe_insert(
                data_path="rotation_euler",
                frame=f
            )

        set_facial_expression(
            c1,
            f,
            mood="happy_wide",
            talk_phase=p * 10
        )

    cam = create_camera(
        "Cam02",
        location=(6.5, -9.5, 2.0),
        rotation=(
            math.radians(96),
            0,
            math.radians(28)
        ),
        lens=28
    )

    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)

        cam.location = (
            6.5,
            -9.5 + p * 3.0,
            2.0 + p * 0.8
        )

        cam.keyframe_insert(
            data_path="location",
            frame=f
        )


def build_scene_03(f_start, f_end):
    clear_scene()

    setup_lighting_and_world(
        sky_color=(0.55, 0.80, 0.98),
        sun_energy=3.5
    )

    mat_wall = get_or_create_material(
        "CabinWall",
        (0.92, 0.94, 0.96),
        roughness=0.4
    )

    mat_floor = get_or_create_material(
        "CabinFloor",
        (0.35, 0.40, 0.48),
        roughness=0.6
    )

    mat_seat = get_or_create_material(
        "CabinSeat",
        (0.12, 0.46, 0.84),
        roughness=0.5
    )

    create_box(
        "Cabin_Floor",
        size=(2.6, 10.0, 0.2),
        location=(0, 0, -0.1),
        mat=mat_floor
    )

    create_box(
        "Cabin_WallL",
        size=(0.15, 10.0, 2.5),
        location=(-1.3, 0, 1.25),
        mat=mat_wall
    )

    create_box(
        "Cabin_Roof",
        size=(2.7, 10.0, 0.2),
        location=(0, 0, 2.5),
        mat=mat_wall
    )

    create_box(
        "Cabin_BenchL",
        size=(0.55, 8.0, 0.45),
        location=(-0.95, 0, 0.22),
        mat=mat_seat,
        bevel_width=0.04
    )

    worker = create_lowpoly_character(
        "Worker",
        location=(-0.85, 0.4, 0.15),
        rotation=(0, 0, math.radians(-85)),
        shirt_color=(0.2, 0.5, 0.8)
    )

    student = create_lowpoly_character(
        "Student",
        location=(-0.85, 1.5, 0.15),
        rotation=(0, 0, math.radians(-95)),
        is_student=True
    )

    for ch in (worker, student):
        ch["torso"].location.z = 0.82
        ch["leg_l"].rotation_euler.x = math.radians(-85)
        ch["leg_r"].rotation_euler.x = math.radians(-85)

    bldg_out = create_box(
        "PassBldg",
        size=(6, 8, 22),
        location=(-8, -15, 5),
        mat=get_or_create_material(
            "OutBldg",
            (0.7, 0.78, 0.88)
        )
    )

    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)

        bldg_out.location.y = -20 + ((p * 80) % 45)

        bldg_out.keyframe_insert(
            data_path="location",
            frame=f
        )

        worker["head_pivot"].rotation_euler.z = (
            math.sin(p * 6.0) * math.radians(12)
        )

        student["head_pivot"].rotation_euler.z = (
            -math.sin(p * 6.0) * math.radians(10)
        )

        worker["head_pivot"].keyframe_insert(
            data_path="rotation_euler",
            frame=f
        )

        student["head_pivot"].keyframe_insert(
            data_path="rotation_euler",
            frame=f
        )

        set_facial_expression(
            worker,
            f,
            mood="smile",
            talk_phase=p * 14
        )

        set_facial_expression(
            student,
            f,
            mood="happy_wide",
            talk_phase=p * 10
        )

    cam = create_camera(
        "Cam03",
        location=(0.65, -1.6, 1.35),
        rotation=(
            math.radians(86),
            0,
            math.radians(22)
        ),
        lens=35
    )

    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)

        cam.location = (
            0.65,
            -1.6 + p * 0.8,
            1.35
        )

        cam.keyframe_insert(
            data_path="location",
            frame=f
        )


def build_scene_04(f_start, f_end):
    clear_scene()

    setup_lighting_and_world(
        sky_color=(0.45, 0.75, 0.98),
        sun_energy=4.2
    )

    build_ground_and_buildings()

    bus1, w1 = create_transjakarta_bus(
        "Bus_North",
        location=(2.8, -15, 0)
    )

    bus2, w2 = create_transjakarta_bus(
        "Bus_South",
        location=(-2.8, 25, 0)
    )

    bus2.rotation_euler.z = math.radians(180)

    car1, cw1 = create_private_car(
        "TidyCar",
        location=(0.2, -22, 0),
        color=(0.25, 0.62, 0.78)
    )

    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)

        bus1.location.y = -15 + p * 35
        bus2.location.y = 25 - p * 35
        car1.location.y = -22 + p * 38

        for obj in (bus1, bus2, car1):
            obj.keyframe_insert(
                data_path="location",
                frame=f
            )

        for w in w1 + w2 + cw1:
            w.rotation_euler.x = -p * 30

            w.keyframe_insert(
                data_path="rotation_euler",
                frame=f
            )

    cam = create_camera(
        "Cam04",
        location=(0, -14, 14),
        rotation=(math.radians(48), 0, 0),
        lens=30
    )

    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)

        cam.location = (
            p * 2.5,
            -14 + p * 4.0,
            14 - p * 2.0
        )

        cam.keyframe_insert(
            data_path="location",
            frame=f
        )


def build_scene_05(f_start, f_end):
    clear_scene()

    world, sun = setup_lighting_and_world(
        sky_color=(0.62, 0.64, 0.66),
        sun_energy=2.2
    )

    build_ground_and_buildings()

    create_lowpoly_tree(
        "Tree05",
        location=(-8.5, 4, 0.15),
        scale=1.2
    )

    hero = create_lowpoly_character(
        "Andra05",
        location=(-7.8, 0, 0.16),
        rotation=(0, 0, math.radians(-20))
    )

    hero["arm_r"].rotation_euler.x = math.radians(-55)

    card = create_box(
        "SavingsCard",
        size=(0.14, 0.02, 0.22),
        location=(0, -0.05, -0.34),
        mat=get_or_create_material(
            "CardGold",
            (0.15, 0.78, 0.45),
            emission_strength=0.4
        ),
        parent=hero["arm_r"]
    )

    bg = world.node_tree.nodes.get("Background")

    for f in range(f_start, f_end + 1, 3):
        p = (f - f_start) / (f_end - f_start)

        if bg:
            r = 0.62 * (1 - p) + 0.42 * p
            g = 0.64 * (1 - p) + 0.76 * p
            b = 0.66 * (1 - p) + 0.98 * p

            bg.inputs["Color"].default_value = (
                r, g, b, 1.0
            )

            bg.inputs["Color"].keyframe_insert(
                data_path="default_value",
                frame=f
            )

        sun.data.energy = 2.2 + p * 2.2

        sun.data.keyframe_insert(
            data_path="energy",
            frame=f
        )

        set_facial_expression(
            hero,
            f,
            mood="happy_wide" if p > 0.4 else "smile",
            talk_phase=p * 10
        )

    cam = create_camera(
        "Cam05",
        location=(-7.3, -2.2, 1.55),
        rotation=(
            math.radians(88),
            0,
            math.radians(-12)
        ),
        lens=42
    )

    for f in (f_start, f_end):
        p = (f - f_start) / (f_end - f_start)

        cam.location = (
            -7.3,
            -2.2 + p * 0.45,
            1.55
        )

        cam.keyframe_insert(
            data_path="location",
            frame=f
        )
