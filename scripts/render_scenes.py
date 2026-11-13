
import os
import bpy


# ==========================================================
# RENDER CONFIGURATION
# ==========================================================

OUTPUT_DIR = os.environ.get(
    "RENDER_OUTPUT_DIR",
    os.path.join(os.getcwd(), "renders", "scenes")
)

RENDER_ENGINE = os.environ.get(
    "RENDER_ENGINE",
    "BLENDER_EEVEE_NEXT"
)

RENDER_SAMPLES = int(
    os.environ.get("RENDER_SAMPLES", "4")
)


# ==========================================================
# SCENE TIMELINE
# ==========================================================
# Pertahankan SCENES_TIMELINE dan BUILDERS asli proyek Anda.
#
# Format:
# SCENES_TIMELINE = [
#     ("scene_01", frame_start, frame_end),
#     ...
#     ("scene_10", frame_start, frame_end),
# ]
#
# Jangan mengganti isi timeline atau builder asli
# dengan contoh angka yang belum diverifikasi.


# ==========================================================
# RENDER SETUP
# ==========================================================

def configure_render(out_mp4, frame_start, frame_end):

    scene = bpy.context.scene

    scene.render.engine = RENDER_ENGINE

    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100

    scene.render.fps = 30

    scene.frame_start = frame_start
    scene.frame_end = frame_end

    # Eevee samples
    if RENDER_ENGINE == "BLENDER_EEVEE_NEXT":
        scene.eevee.taa_render_samples = RENDER_SAMPLES

    # Video output
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"

    scene.render.filepath = out_mp4

    scene.render.use_file_extension = True

    # Disable unnecessary output
    scene.render.use_overwrite = True

    print(f"ENGINE: {RENDER_ENGINE}", flush=True)
    print(f"SAMPLES: {RENDER_SAMPLES}", flush=True)
    print(f"OUTPUT: {out_mp4}", flush=True)


# ==========================================================
# MAIN RENDER PROCESS
# ==========================================================

def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ------------------------------------------------------
    # VALIDATE SCENE DEFINITIONS
    # ------------------------------------------------------

    valid_scenes = {
        scene_id
        for scene_id, _, _ in SCENES_TIMELINE
    }

    if len(valid_scenes) != len(SCENES_TIMELINE):
        raise RuntimeError(
            "Terdapat scene ID duplikat dalam SCENES_TIMELINE."
        )

    # ------------------------------------------------------
    # SELECT SCENES
    # ------------------------------------------------------

    raw_filter = os.environ.get(
        "SCENE_FILTER",
        ""
    ).strip()

    if raw_filter:
        scene_filter = {
            item.strip()
            for item in raw_filter.split(",")
            if item.strip()
        }
    else:
        scene_filter = valid_scenes.copy()

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
        raise RuntimeError(
            "Tidak ada scene yang dipilih!"
        )

    # ------------------------------------------------------
    # START LOG
    # ------------------------------------------------------

    print("\n" + "=" * 60)
    print("JAKARTA LOW-POLY 3D RENDER")
    print("SINGLE JOB - SEQUENTIAL RENDER")
    print("=" * 60)

    print(f"Render Engine : {RENDER_ENGINE}")
    print(f"Samples       : {RENDER_SAMPLES}")
    print(f"Total Scenes  : {len(selected_scenes)}")
    print(f"Output Dir    : {OUTPUT_DIR}")

    print(
        "Scene List   :",
        [scene[0] for scene in selected_scenes]
    )

    print("=" * 60 + "\n", flush=True)

    # ------------------------------------------------------
    # RENDER ALL SCENES SEQUENTIALLY
    # ------------------------------------------------------

    for index, (scene_id, f_start, f_end) in enumerate(
        selected_scenes,
        start=1
    ):

        print("\n" + "-" * 60, flush=True)

        print(
            f"[SCENE {index}/{len(selected_scenes)}] "
            f"BUILDING {scene_id}",
            flush=True
        )

        print(
            f"Frames: {f_start} - {f_end - 1}",
            flush=True
        )

        print("-" * 60, flush=True)

        # --------------------------------------------------
        # BUILD SCENE
        # --------------------------------------------------

        if scene_id not in BUILDERS:
            raise RuntimeError(
                f"Builder tidak ditemukan: {scene_id}"
            )

        BUILDERS[scene_id](
            f_start,
            f_end - 1
        )

        # --------------------------------------------------
        # MP4 OUTPUT
        # --------------------------------------------------

        out_mp4 = os.path.join(
            OUTPUT_DIR,
            f"{scene_id}.mp4"
        )

        os.makedirs(
            os.path.dirname(out_mp4),
            exist_ok=True
        )

        # --------------------------------------------------
        # CONFIGURE RENDER
        # --------------------------------------------------

        configure_render(
            out_mp4,
            f_start,
            f_end - 1
        )

        print(
            f"MP4 TARGET: {out_mp4}",
            flush=True
        )

        # --------------------------------------------------
        # START RENDER
        # --------------------------------------------------

        print(
            f"START RENDER: {scene_id}",
            flush=True
        )

        bpy.ops.render.render(
            animation=True
        )

        # --------------------------------------------------
        # VERIFY OUTPUT
        # --------------------------------------------------

        if not os.path.isfile(out_mp4):
            raise RuntimeError(
                f"File hasil render tidak ditemukan: {out_mp4}"
            )

        file_size = os.path.getsize(out_mp4)

        if file_size == 0:
            raise RuntimeError(
                f"File hasil render kosong: {out_mp4}"
            )

        print(
            f"SUCCESS: {scene_id} selesai!",
            flush=True
        )

        print(
            f"OUTPUT: {out_mp4}",
            flush=True
        )

        print(
            f"FILE SIZE: {file_size} bytes",
            flush=True
        )

        print(
            f"PROGRESS: {index}/{len(selected_scenes)}",
            flush=True
        )

    # ------------------------------------------------------
    # FINAL VERIFICATION
    # ------------------------------------------------------

    print("\n" + "=" * 60)
    print("VERIFYING ALL RENDERED SCENES")
    print("=" * 60, flush=True)

    for scene_id, _, _ in selected_scenes:

        out_mp4 = os.path.join(
            OUTPUT_DIR,
            f"{scene_id}.mp4"
        )

        if not os.path.isfile(out_mp4):
            raise RuntimeError(
                f"Scene belum berhasil dirender: {scene_id}"
            )

        if os.path.getsize(out_mp4) == 0:
            raise RuntimeError(
                f"Output scene kosong: {scene_id}"
            )

        print(
            f"VERIFIED: {scene_id}.mp4 "
            f"({os.path.getsize(out_mp4)} bytes)",
            flush=True
        )

    print("\n" + "=" * 60)
    print("ALL SCENES RENDERED SUCCESSFULLY!")
    print(f"TOTAL: {len(selected_scenes)} SCENES")
    print("RENDER MODE: SINGLE JOB")
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
