    valid_scenes = {scene_id for scene_id, _, _ in SCENES_TIMELINE}
    invalid_scenes = scene_filter - valid_scenes

    if invalid_scenes:
        raise ValueError(f"Scene tidak dikenal: {sorted(invalid_scenes)}")

    selected_scenes = [
        item for item in SCENES_TIMELINE if item[0] in scene_filter
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
    print(f"Output Dir    : {OUTPUT_DIR}")
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
        out_mp4 = os.path.join(OUTPUT_DIR, f"{scene_id}.mp4")

        # Pastikan direktori output tersedia sebelum Blender mulai render.
        os.makedirs(os.path.dirname(out_mp4), exist_ok=True)

        # Configure render
        configure_render(
            out_mp4,
            f_start,
            f_end - 1
        )
        print(f"MP4 TARGET: {out_mp4}", flush=True)

        # Render animation
        print(
            f"START RENDER: {scene_id}",
            flush=True
        )

        bpy.ops.render.render(animation=True)

        # Diagnostik: tampilkan file yang benar-benar dibuat Blender.
        print(f"OUTPUT DIRECTORY CONTENTS: {os.listdir(OUTPUT_DIR)}", flush=True)

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
