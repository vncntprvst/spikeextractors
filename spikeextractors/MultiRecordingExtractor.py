from .RecordingExtractor import RecordingExtractor
import numpy as np


class MultiRecordingExtractor(RecordingExtractor):
    def __init__(self, recordings, epoch_names=None):
        RecordingExtractor.__init__(self)
        if epoch_names is None:
            epoch_names = [str(i) for i in range(len(recordings))]

        # Add all epochs to the epochs data structure
        start_frames = 0
        for i, epoch_name in enumerate(epoch_names):
            num_frames = recordings[i].get_num_frames()
            self.add_epoch(epoch_name, start_frames, start_frames + num_frames)
            start_frames += num_frames

        self._RXs = recordings

        # Num channels and sampling frequency based off the initial extractor
        self._first_recording = recordings[0]
        self._num_channels = self._first_recording.get_num_channels()
        self._channel_ids = self._first_recording.get_channel_ids()
        self._sampling_frequency = self._first_recording.get_sampling_frequency()

        # Test if all recording extractors have same num channels and sampling frequency
        for i, recording in enumerate(recordings[1:]):
            channel_ids = recording.get_channel_ids()
            sampling_frequency = recording.get_sampling_frequency()

            if (self._channel_ids != channel_ids):
                raise ValueError("Inconsistent channel ids between extractor 0 and extractor " + str(i + 1))
            if (self._sampling_frequency != sampling_frequency):
                raise ValueError("Inconsistent sampling frequency between extractor 0 and extractor " + str(i + 1))

        self._start_frames = []
        self._start_times = []
        ff = 0
        tt = 0
        for RX in self._RXs:
            self._start_frames.append(ff)
            ff = ff + RX.get_num_frames()
            tt = tt + RX.frame_to_time(0)
            self._start_times.append(tt)
            tt = tt + RX.frame_to_time(RX.get_num_frames()) - RX.frame_to_time(0)
        self._start_frames.append(ff)
        self._start_times.append(tt)
        self._num_frames = ff

        # Set the channel properties based on the first recording extractor
        self.copy_channel_properties(self._first_recording)

    def _find_section_for_frame(self, frame):
        inds = np.where(np.array(self._start_frames[:-1]) <= frame)[0]
        ind = inds[-1]
        return self._RXs[ind], ind, frame - self._start_frames[ind]

    def _find_section_for_time(self, time):
        inds = np.where(np.array(self._start_times[:-1]) <= time)[0]
        ind = inds[-1]
        return self._RXs[ind], ind, time - self._start_times[ind]

    def get_traces(self, channel_ids=None, start_frame=None, end_frame=None):
        if start_frame is None:
            start_frame = 0
        if end_frame is None:
            end_frame = self.get_num_frames()
        RX1, i_sec1, i_start_frame = self._find_section_for_frame(start_frame)
        RX2, i_sec2, i_end_frame = self._find_section_for_frame(end_frame)
        if i_sec1 == i_sec2:
            return RX1.get_traces(channel_ids=channel_ids, start_frame=i_start_frame, end_frame=i_end_frame)
        list = []
        list.append(
            self._RXs[i_sec1].get_traces(channel_ids=channel_ids, start_frame=i_start_frame,
                                         end_frame=self._RXs[i_sec1].get_num_frames())
        )
        for i_sec in range(i_sec1 + 1, i_sec2):
            list.append(
                self._RXs[i_sec].get_traces(channel_ids=channel_ids)
            )
        list.append(
            self._RXs[i_sec2].get_traces(channel_ids=channel_ids, start_frame=0, end_frame=i_end_frame)
        )
        return np.concatenate(list, axis=1)

    def get_channel_ids(self):
        return self._channel_ids

    def get_num_frames(self):
        return self._num_frames

    def get_sampling_frequency(self):
        return self._sampling_frequency

    def frame_to_time(self, frame):
        RX, i_epoch, rel_frame = self._find_section_for_frame(frame)
        return RX.frame_to_time(rel_frame) + self._start_times[i_epoch]

    def time_to_frame(self, time):
        RX, i_epoch, rel_time = self._find_section_for_time(time)
        return RX.time_to_frame(rel_time) + self._start_frames[i_epoch]
