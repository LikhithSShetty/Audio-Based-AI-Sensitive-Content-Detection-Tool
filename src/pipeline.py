def run_pipeline(video_file, criteria):
    from transcription.transcribe import Transcriber
    from identification.identify import Identifier
    from redaction.redact import Redactor

    # Step 1: Transcribe the video
    transcriber = Transcriber()
    transcriber.transcribe_video(video_file)
    transcript = transcriber.get_transcript()

    # Step 2: Identify sensitive content
    identifier = Identifier()
    identifier.identify_sensitive_content(transcript, criteria)
    flagged_segments = identifier.get_flagged_segments()

    # Step 3: Redact sensitive segments from the video
    redactor = Redactor()
    redacted_video = redactor.redact_video(video_file, flagged_segments)
    redactor.save_redacted_video(redacted_video)

    return redacted_video