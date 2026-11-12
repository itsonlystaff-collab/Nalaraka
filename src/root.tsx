import React from 'react';
import {Composition} from 'remotion';
import {FPS, TOTAL_FRAMES, VideoShort} from './video/VideoShort';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="VideoShort"
      component={VideoShort}
      durationInFrames={TOTAL_FRAMES}
      fps={FPS}
      width={1080}
      height={1920}
    />
  );
};
