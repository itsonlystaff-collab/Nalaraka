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
    output_dir = os.environ.get(
        "RENDER_OUTPUT_DIR",
        os.path.abspath(os.path.join(os.getcwd(), "renders", "scenes"))
    )
    os.makedirs(output_dir, exist_ok=True)

    valid_scenes = {scene_id for scene_id, _, _ in SCENES_TIMELINE}
    if len(valid_scenes) != len(SCENES_TIMELINE):
        raise RuntimeError("Terdapat scene ID duplikat dalam SCENES_TIMELINE.")

    missing_builders = valid_scenes - set(BUILDERS.keys())
    if missing_builders:
        raise RuntimeError(
            f"Builder tidak ditemukan untuk scene: {sorted(missing_builders)}"
        )

    raw_filter = os.environ.get("SCENE_FILTER", "").strip()
    if raw_filter:
        scene_filter = {
            item.strip() for item in raw_filter.split(",") if item.strip()
        }
    else:
        scene_filter = valid_scenes.copy()

    invalid_scenes = scene_filter - valid_scenes
    if invalid_scenes:
        raise ValueError(f"Scene tidak dikenal: {sorted(invalid_scenes)}")

    selected_scenes = [
        item for item in SCENES_TIMELINE if item[0] in scene_filter
    ]
    if not selected_scenes:
        raise RuntimeError("Tidak ada scene yang dipilih!")

    engine = os.environ.get("RENDER_ENGINE", "BLENDER_EEVEE_NEXT")
    samples = max(4, int(os.environ.get("RENDER_SAMPLES", "4")))

    print("\\n" + "=" * 60)
    print("JAKARTA LOW-POLY 3D RENDER")
    print("SINGLE JOB - SEQUENTIAL RENDER")
    print(f"ENGINE: {engine}")
    print(f"SAMPLES: {samples}")
    print(f"TOTAL SCENES: {len(selected_scenes)}")
    print(f"OUTPUT: {output_dir}")
    print("SCENES:", [item[0] for item in selected_scenes])
    print("=" * 60, flush=True)

    for index, (scene_id, frame_start, frame_end_exclusive) in enumerate(
        selected_scenes, start=1
    ):
        frame_end = frame_end_exclusive - 1
        print("\\n" + "-" * 60, flush=True)
        print(f"[SCENE {index}/{len(selected_scenes)}] BUILDING {scene_id}", flush=True)
        print(f"FRAMES: {frame_start} - {frame_end}", flush=True)

        BUILDERS[scene_id](frame_start, frame_end)

        output_filepath = os.path.join(output_dir, f"{scene_id}.mp4")
        configure_render(output_filepath, frame_start, frame_end)

        print(f"START RENDER: {scene_id}", flush=True)
        bpy.ops.render.render(animation=True)

        if not os.path.isfile(output_filepath):
            alternate_path = output_filepath + ".mp4"
            if os.path.isfile(alternate_path):
                output_filepath = alternate_path

        if not os.path.isfile(output_filepath):
            raise RuntimeError(f"File hasil render tidak ditemukan: {output_filepath}")

        file_size = os.path.getsize(output_filepath)
        if file_size <= 0:
            raise RuntimeError(f"Output scene kosong: {output_filepath}")

        print(f"SUCCESS: {scene_id}", flush=True)
        print(f"OUTPUT: {output_filepath}", flush=True)
        print(f"FILE SIZE: {file_size} bytes", flush=True)
        print(f"PROGRESS: {index}/{len(selected_scenes)}", flush=True)

    print("\\n" + "=" * 60)
    print("VERIFYING ALL RENDERED SCENES")
    print("=" * 60, flush=True)

    for scene_id, _, _ in selected_scenes:
        output_filepath = os.path.join(output_dir, f"{scene_id}.mp4")
        if not os.path.isfile(output_filepath):
            alternate_path = output_filepath + ".mp4"
            if os.path.isfile(alternate_path):
                output_filepath = alternate_path

        if not os.path.isfile(output_filepath):
            raise RuntimeError(f"Scene belum berhasil dirender: {scene_id}")

        size = os.path.getsize(output_filepath)
        if size <= 0:
            raise RuntimeError(f"Output scene kosong: {output_filepath}")

        print(f"VERIFIED: {os.path.basename(output_filepath)} ({size} bytes)", flush=True)

    print("\\n" + "=" * 60)
    print("ALL SCENES RENDERED SUCCESSFULLY!")
    print(f"TOTAL: {len(selected_scenes)} SCENES")
    print("RENDER MODE: SINGLE JOB")
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
