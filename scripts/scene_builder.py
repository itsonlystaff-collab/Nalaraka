import bpy
import bmesh
import math
from mathutils import Vector, Euler

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def get_or_create_material(name, color, roughness=0.65, metallic=0.0, emission_strength=0.0, alpha=1.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission_strength > 0:
            bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emission_strength
        if alpha < 1.0:
            bsdf.inputs["Alpha"].default_value = alpha
    return mat

def set_flat_shading(obj):
    if obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth = False

def create_box(name, size=(1, 1, 1), location=(0, 0, 0), rotation=(0, 0, 0), mat=None, parent=None, bevel_width=0.03):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    if bevel_width > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel_width, segments=1, affect='EDGES')
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    if mat:
        obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    set_flat_shading(obj)
    return obj

def create_cylinder(name, radius=0.5, depth=1.0, vertices=8, location=(0, 0, 0), rotation=(0, 0, 0), mat=None, parent=None):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=vertices, radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    if mat:
        obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    set_flat_shading(obj)
    return obj

def create_icosphere(name, radius=0.5, subdivisions=1, location=(0, 0, 0), scale=(1, 1, 1), mat=None, parent=None):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=radius)
    bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    if mat:
        obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    set_flat_shading(obj)
    return obj

def create_lowpoly_character(name="Citizen", location=(0, 0, 0), rotation=(0, 0, 0), shirt_color=(0.15, 0.45, 0.85), pants_color=(0.14, 0.16, 0.22), is_student=False):
    """
    Membangun karakter Low-Poly dengan hierarki bagian bergerak independen (kepala, badan, lengan, kaki)
    serta ekspresi wajah lengkap: mata berkedip (eyelids), alis ekspresif (brows), dan mulut animasi (smile/talk/inhale).
    """
    root = bpy.data.objects.new(name + "_Root", None)
    bpy.context.collection.objects.link(root)
    root.location = location
    root.rotation_euler = rotation

    mat_skin = get_or_create_material("Skin_Mat", (0.87, 0.67, 0.52), roughness=0.55)
    mat_hair = get_or_create_material("Hair_Mat", (0.08, 0.07, 0.07), roughness=0.75)
    mat_shirt = get_or_create_material(f"Shirt_{name}", (0.95, 0.96, 0.98) if is_student else shirt_color, roughness=0.7)
    mat_pants = get_or_create_material(f"Pants_{name}", (0.12, 0.24, 0.48) if is_student else pants_color, roughness=0.75)
    mat_shoe = get_or_create_material("Shoe_Mat", (0.1, 0.1, 0.12), roughness=0.5)
    mat_eye_white = get_or_create_material("EyeWhite_Mat", (0.98, 0.98, 0.98), roughness=0.2)
    mat_pupil = get_or_create_material("Pupil_Mat", (0.04, 0.04, 0.05), roughness=0.1)
    mat_mouth = get_or_create_material("Mouth_Mat", (0.65, 0.22, 0.24), roughness=0.4)

    # Legs (pivot di pinggul z=0.82)
    leg_l = create_box(name + "_LegL", size=(0.16, 0.18, 0.72), location=(-0.11, 0, 0.46), mat=mat_pants, parent=root, bevel_width=0.02)
    leg_r = create_box(name + "_LegR", size=(0.16, 0.18, 0.72), location=(0.11, 0, 0.46), mat=mat_pants, parent=root, bevel_width=0.02)
    create_box(name + "_ShoeL", size=(0.17, 0.26, 0.10), location=(0, -0.04, -0.36), mat=mat_shoe, parent=leg_l, bevel_width=0.02)
    create_box(name + "_ShoeR", size=(0.17, 0.26, 0.10), location=(0, -0.04, -0.36), mat=mat_shoe, parent=leg_r, bevel_width=0.02)

    # Torso (z=0.82 -> 1.42)
    torso = create_box(name + "_Torso", size=(0.44, 0.26, 0.60), location=(0, 0, 1.12), mat=mat_shirt, parent=root, bevel_width=0.04)

    # Backpack / Tas
    bag_color = (0.85, 0.28, 0.18) if is_student else (0.22, 0.25, 0.30)
    mat_bag = get_or_create_material(f"Bag_{name}", bag_color, roughness=0.7)
    create_box(name + "_Backpack", size=(0.34, 0.16, 0.42), location=(0, 0.19, 0.02), mat=mat_bag, parent=torso, bevel_width=0.03)

    # Arms (pivot di bahu)
    arm_l = create_box(name + "_ArmL", size=(0.13, 0.14, 0.54), location=(-0.30, 0, 0.02), mat=mat_shirt, parent=torso, bevel_width=0.02)
    arm_r = create_box(name + "_ArmR", size=(0.13, 0.14, 0.54), location=(0.30, 0, 0.02), mat=mat_shirt, parent=torso, bevel_width=0.02)
    create_box(name + "_HandL", size=(0.11, 0.11, 0.12), location=(0, 0, -0.30), mat=mat_skin, parent=arm_l, bevel_width=0.02)
    create_box(name + "_HandR", size=(0.11, 0.11, 0.12), location=(0, 0, -0.30), mat=mat_skin, parent=arm_r, bevel_width=0.02)

    # Head Group (pivot di leher z=1.45)
    head_pivot = bpy.data.objects.new(name + "_HeadPivot", None)
    bpy.context.collection.objects.link(head_pivot)
    head_pivot.location = (0, 0, 0.34)
    head_pivot.parent = torso

    head = create_box(name + "_Head", size=(0.38, 0.38, 0.40), location=(0, 0, 0.22), mat=mat_skin, parent=head_pivot, bevel_width=0.06)

    # Low-Poly Hair Cap
    create_box(name + "_HairTop", size=(0.41, 0.41, 0.14), location=(0, 0.01, 0.17), mat=mat_hair, parent=head, bevel_width=0.04)
    create_box(name + "_HairBack", size=(0.40, 0.12, 0.30), location=(0, 0.16, 0.03), mat=mat_hair, parent=head, bevel_width=0.03)

    # Nose
    create_box(name + "_Nose", size=(0.05, 0.06, 0.07), location=(0, -0.20, -0.01), mat=mat_skin, parent=head, bevel_width=0.015)

    # Facial Expression Rig Parts (Mata, Kelopak Kedip, Alis, Mulut 3-segmen untuk senyum/bicara/kagum)
    eye_l = create_box(name + "_EyeL", size=(0.075, 0.03, 0.075), location=(-0.09, -0.185, 0.04), mat=mat_eye_white, parent=head, bevel_width=0.01)
    eye_r = create_box(name + "_EyeR", size=(0.075, 0.03, 0.075), location=(0.09, -0.185, 0.04), mat=mat_eye_white, parent=head, bevel_width=0.01)

    pupil_l = create_box(name + "_PupilL", size=(0.04, 0.02, 0.045), location=(0, -0.012, 0), mat=mat_pupil, parent=eye_l, bevel_width=0.005)
    pupil_r = create_box(name + "_PupilR", size=(0.04, 0.02, 0.045), location=(0, -0.012, 0), mat=mat_pupil, parent=eye_r, bevel_width=0.005)

    # Eyelids (untuk ekspresi berkedip & mata terpejam segar)
    eyelid_l = create_box(name + "_EyelidL", size=(0.082, 0.036, 0.082), location=(-0.09, -0.188, 0.04), mat=mat_skin, parent=head, bevel_width=0.01)
    eyelid_r = create_box(name + "_EyelidR", size=(0.082, 0.036, 0.082), location=(0.09, -0.188, 0.04), mat=mat_skin, parent=head, bevel_width=0.01)
    eyelid_l.scale = (1.0, 1.0, 0.05)
    eyelid_r.scale = (1.0, 1.0, 0.05)

    # Eyebrows (Alis untuk ekspresi optimis, antusias, lega)
    brow_l = create_box(name + "_BrowL", size=(0.095, 0.03, 0.024), location=(-0.09, -0.195, 0.105), mat=mat_hair, parent=head, bevel_width=0.005)
    brow_r = create_box(name + "_BrowR", size=(0.095, 0.03, 0.024), location=(0.09, -0.195, 0.105), mat=mat_hair, parent=head, bevel_width=0.005)

    # Mouth (Tengah + Sudut Kiri & Kanan untuk membentuk senyum lebar, bicara, atau takjub)
    mouth_mid = create_box(name + "_MouthMid", size=(0.08, 0.025, 0.024), location=(0, -0.192, -0.085), mat=mat_mouth, parent=head, bevel_width=0.005)
    mouth_l = create_box(name + "_MouthCornerL", size=(0.04, 0.025, 0.022), location=(-0.055, -0.192, -0.080), mat=mat_mouth, parent=head, bevel_width=0.005)
    mouth_r = create_box(name + "_MouthCornerR", size=(0.04, 0.025, 0.022), location=(0.055, -0.192, -0.080), mat=mat_mouth, parent=head, bevel_width=0.005)

    return {
        "root": root,
        "torso": torso,
        "head_pivot": head_pivot,
        "head": head,
        "leg_l": leg_l,
        "leg_r": leg_r,
        "arm_l": arm_l,
        "arm_r": arm_r,
        "eyelid_l": eyelid_l,
        "eyelid_r": eyelid_r,
        "brow_l": brow_l,
        "brow_r": brow_r,
        "mouth_mid": mouth_mid,
        "mouth_l": mouth_l,
        "mouth_r": mouth_r,
    }

def set_facial_expression(char_dict, frame, mood="smile", talk_phase=0.0):
    """
    Mengatur ekspresi wajah karakter berdasarkan mood ('smile', 'happy_wide', 'calm_inhale', 'amazed', 'neutral')
    dan siklus kedipan alami setiap ~90 frame (3 detik).
    """
    blink_cycle = frame % 95
    if 0 <= blink_cycle <= 3:
        lid_z = 1.0
    elif 4 <= blink_cycle <= 6:
        lid_z = 0.4
    else:
        lid_z = 0.05

    if mood == "calm_inhale":
        # Mata terpejam rileks menghirup udara segar
        lid_z = 0.95

    for lid in (char_dict["eyelid_l"], char_dict["eyelid_r"]):
        lid.scale.z = lid_z
        lid.keyframe_insert(data_path="scale", frame=frame)

    bl = char_dict["brow_l"]
    br = char_dict["brow_r"]
    mm = char_dict["mouth_mid"]
    ml = char_dict["mouth_l"]
    mr = char_dict["mouth_r"]

    talk_open = 1.0 + 0.8 * max(0.0, math.sin(talk_phase))

    if mood == "happy_wide":
        bl.location.z = 0.118
        br.location.z = 0.118
        bl.rotation_euler.y = math.radians(-8)
        br.rotation_euler.y = math.radians(8)
        mm.scale = (1.25, 1.0, 1.6 * talk_open)
        ml.location.z = -0.068
        mr.location.z = -0.068
        ml.rotation_euler.y = math.radians(-22)
        mr.rotation_euler.y = math.radians(22)
    elif mood == "amazed":
        bl.location.z = 0.125
        br.location.z = 0.125
        bl.rotation_euler.y = math.radians(-10)
        br.rotation_euler.y = math.radians(10)
        mm.scale = (0.85, 1.0, 2.2)
        ml.location.z = -0.075
        mr.location.z = -0.075
        ml.rotation_euler.y = math.radians(-12)
        mr.rotation_euler.y = math.radians(12)
    elif mood == "calm_inhale":
        bl.location.z = 0.112
        br.location.z = 0.112
        bl.rotation_euler.y = math.radians(-4)
        br.rotation_euler.y = math.radians(4)
        mm.scale = (1.15, 1.0, 1.1)
        ml.location.z = -0.072
        mr.location.z = -0.072
        ml.rotation_euler.y = math.radians(-18)
        mr.rotation_euler.y = math.radians(18)
    else:  # "smile"
        bl.location.z = 0.110
        br.location.z = 0.110
        bl.rotation_euler.y = math.radians(-5)
        br.rotation_euler.y = math.radians(5)
        mm.scale = (1.1, 1.0, 1.15 * talk_open)
        ml.location.z = -0.073
        mr.location.z = -0.073
        ml.rotation_euler.y = math.radians(-16)
        mr.rotation_euler.y = math.radians(16)

    for obj in (bl, br, mm, ml, mr):
        obj.keyframe_insert(data_path="location", frame=frame)
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
        obj.keyframe_insert(data_path="scale", frame=frame)

def animate_walk_cycle(char_dict, start_frame, end_frame, speed=1.0):
    for f in range(start_frame, end_frame + 1, 3):
        t = (f - start_frame) / 30.0
        swing = math.sin(t * 7.5 * speed) * math.radians(26)
        char_dict["leg_l"].rotation_euler.x = swing
        char_dict["leg_r"].rotation_euler.x = -swing
        char_dict["arm_l"].rotation_euler.x = -swing * 0.75
        char_dict["arm_r"].rotation_euler.x = swing * 0.75
        char_dict["torso"].location.z = 1.12 + abs(math.cos(t * 7.5 * speed)) * 0.03

        for part in ("leg_l", "leg_r", "arm_l", "arm_r"):
            char_dict[part].keyframe_insert(data_path="rotation_euler", frame=f)
        char_dict["torso"].keyframe_insert(data_path="location", frame=f)

def create_lowpoly_tree(name="Tree", location=(0, 0, 0), scale=1.0):
    root = bpy.data.objects.new(name + "_Root", None)
    bpy.context.collection.objects.link(root)
    root.location = location
    root.scale = (scale, scale, scale)

    mat_trunk = get_or_create_material("Trunk_Mat", (0.36, 0.22, 0.12), roughness=0.85)
    mat_leaf1 = get_or_create_material("Leaf1_Mat", (0.16, 0.56, 0.24), roughness=0.7)
    mat_leaf2 = get_or_create_material("Leaf2_Mat", (0.24, 0.68, 0.30), roughness=0.7)

    create_cylinder(name + "_Trunk", radius=0.16, depth=1.6, vertices=7, location=(0, 0, 0.8), mat=mat_trunk, parent=root)
    canopy1 = create_icosphere(name + "_Canopy1", radius=0.95, subdivisions=1, location=(0, 0, 2.0), scale=(1.1, 1.1, 0.9), mat=mat_leaf1, parent=root)
    canopy2 = create_icosphere(name + "_Canopy2", radius=0.72, subdivisions=1, location=(0.35, -0.2, 2.55), scale=(1.0, 1.0, 0.85), mat=mat_leaf2, parent=root)
    return root, canopy1, canopy2

def create_mrt_train(name="MRT_Ratangga", location=(0, 0, 0)):
    root = bpy.data.objects.new(name + "_Root", None)
    bpy.context.collection.objects.link(root)
    root.location = location

    mat_body = get_or_create_material("MRT_White", (0.94, 0.96, 0.98), roughness=0.35, metallic=0.1)
    mat_blue = get_or_create_material("MRT_Blue", (0.06, 0.35, 0.78), roughness=0.35)
    mat_glass = get_or_create_material("Glass_Dark", (0.08, 0.14, 0.22), roughness=0.15, metallic=0.4)

    for i in range(3):
        y_off = i * 6.4
        car = create_box(f"{name}_Car_{i}", size=(2.6, 6.0, 2.8), location=(0, y_off, 1.6), mat=mat_body, parent=root, bevel_width=0.12)
        create_box(f"{name}_Stripe_{i}", size=(2.64, 6.02, 0.55), location=(0, y_off, 0.95), mat=mat_blue, parent=root, bevel_width=0.05)
        create_box(f"{name}_Win_{i}", size=(2.66, 5.2, 0.85), location=(0, y_off, 1.95), mat=mat_glass, parent=root, bevel_width=0.03)
    return root

def create_transjakarta_bus(name="TransJakarta", location=(0, 0, 0)):
    root = bpy.data.objects.new(name + "_Root", None)
    bpy.context.collection.objects.link(root)
    root.location = location

    mat_white = get_or_create_material("TJ_White", (0.95, 0.96, 0.98), roughness=0.4)
    mat_blue = get_or_create_material("TJ_Blue", (0.05, 0.32, 0.72), roughness=0.4)
    mat_glass = get_or_create_material("Glass_Dark", (0.08, 0.14, 0.22), roughness=0.15, metallic=0.4)
    mat_tire = get_or_create_material("Tire_Mat", (0.08, 0.08, 0.09), roughness=0.8)

    create_box(name + "_Body", size=(2.4, 7.2, 2.6), location=(0, 0, 1.65), mat=mat_white, parent=root, bevel_width=0.1)
    create_box(name + "_Lower", size=(2.44, 7.24, 0.85), location=(0, 0, 0.85), mat=mat_blue, parent=root, bevel_width=0.06)
    create_box(name + "_Windows", size=(2.46, 6.4, 0.95), location=(0, 0, 2.05), mat=mat_glass, parent=root, bevel_width=0.03)

    wheels = []
    for wx in (-1.15, 1.15):
        for wy in (-2.2, 2.2):
            w = create_cylinder(f"{name}_Wheel_{wx}_{wy}", radius=0.48, depth=0.32, vertices=12,
                                location=(wx, wy, 0.48), rotation=(0, math.radians(90), 0), mat=mat_tire, parent=root)
            wheels.append(w)
    return root, wheels

def create_private_car(name="Car", location=(0, 0, 0), color=(0.82, 0.22, 0.20)):
    root = bpy.data.objects.new(name + "_Root", None)
    bpy.context.collection.objects.link(root)
    root.location = location

    mat_car = get_or_create_material(f"CarMat_{name}", color, roughness=0.35, metallic=0.2)
    mat_glass = get_or_create_material("Glass_Dark", (0.08, 0.14, 0.22), roughness=0.15, metallic=0.4)
    mat_tire = get_or_create_material("Tire_Mat", (0.08, 0.08, 0.09), roughness=0.8)

    create_box(name + "_Chassis", size=(1.8, 3.8, 0.75), location=(0, 0, 0.65), mat=mat_car, parent=root, bevel_width=0.08)
    create_box(name + "_Cabin", size=(1.55, 2.0, 0.68), location=(0, 0.15, 1.32), mat=mat_glass, parent=root, bevel_width=0.08)

    wheels = []
    for wx in (-0.88, 0.88):
        for wy in (-1.15, 1.15):
            w = create_cylinder(f"{name}_Wheel_{wx}_{wy}", radius=0.34, depth=0.24, vertices=10,
                                location=(wx, wy, 0.34), rotation=(0, math.radians(90), 0), mat=mat_tire, parent=root)
            wheels.append(w)
    return root, wheels

def create_monas_landmark(location=(0, 45, 0)):
    root = bpy.data.objects.new("Monas_Root", None)
    bpy.context.collection.objects.link(root)
    root.location = location

    mat_marble = get_or_create_material("Monas_Marble", (0.94, 0.93, 0.90), roughness=0.45)
    mat_gold = get_or_create_material("Monas_Gold", (0.98, 0.76, 0.12), roughness=0.25, metallic=0.85, emission_strength=0.6)

    create_box("Monas_Base", size=(10.0, 10.0, 2.5), location=(0, 0, 1.25), mat=mat_marble, parent=root, bevel_width=0.15)
    create_box("Monas_Cup", size=(6.5, 6.5, 1.8), location=(0, 0, 3.2), mat=mat_marble, parent=root, bevel_width=0.1)
    create_box("Monas_Obelisk", size=(2.2, 2.2, 18.0), location=(0, 0, 13.0), mat=mat_marble, parent=root, bevel_width=0.08)
    create_icosphere("Monas_Flame", radius=1.1, subdivisions=1, location=(0, 0, 23.0), scale=(0.8, 0.8, 1.4), mat=mat_gold, parent=root)
    return root

def setup_lighting_and_world(sky_color=(0.45, 0.72, 0.96), sun_energy=3.8, fog_density=0.0):
    world = bpy.data.worlds.new("JakartaWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (*sky_color, 1.0)
        bg.inputs["Strength"].default_value = 0.85

    # Key Light (Sun dengan bayangan tajam namun lembut)
    sun_data = bpy.data.lights.new(name="SunKey", type='SUN')
    sun_data.energy = sun_energy
    sun_data.angle = math.radians(2.5)
    sun_obj = bpy.data.objects.new(name="SunKey", object_data=sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(52), math.radians(15), math.radians(-35))

    # Fill Light
    fill_data = bpy.data.lights.new(name="FillArea", type='AREA')
    fill_data.energy = 120.0
    fill_data.size = 12.0
    fill_data.color = (0.75, 0.86, 1.0)
    fill_obj = bpy.data.objects.new(name="FillArea", object_data=fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-10, -8, 9)
    fill_obj.rotation_euler = (math.radians(60), 0, math.radians(-45))

    return world, sun_obj
