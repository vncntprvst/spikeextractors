from abc import ABC, abstractmethod
import numpy as np
import copy


class SortingExtractor(ABC):
    '''A class that contains functions for extracting important information
    from spiked sorted data given a spike sorting software. It is an abstract
    class so all functions with the @abstractmethod tag must be implemented for
    the initialization to work.


    '''
    extractor_name = ''
    installed = False  # check at class level if installed or not
    _gui_params = []
    installation_mesg = ""  # error message when not installed

    def __init__(self):
        self._unit_properties = {}
        self._unit_features = {}

    @abstractmethod
    def get_unit_ids(self):
        '''This function returns a list of ids (ints) for each unit in the recording.

        Returns
        ----------
        unit_ids: array_like
            A list or 1D array of the unit ids in recording (ints).
        '''
        pass

    @abstractmethod
    def get_unit_spike_train(self, unit_id, start_frame=None, end_frame=None):
        '''This function extracts spike frames from the specified unit.
        It will return spike frames from within three ranges:

            [start_frame, t_start+1, ..., end_frame-1]
            [start_frame, start_frame+1, ..., final_unit_spike_frame - 1]
            [0, 1, ..., end_frame-1]
            [0, 1, ..., final_unit_spike_frame - 1]

        if both start_frame and end_frame are given, if only start_frame is
        given, if only end_frame is given, or if neither start_frame or end_frame
        are given, respectively. Spike frames are returned in the form of an
        array_like of spike frames. In this implementation, start_frame is inclusive
        and end_frame is exclusive conforming to numpy standards.

        Parameters
        ----------
        unit_id: int
            The id that specifies a unit in the recording.
        start_frame: int
            The frame above which a spike frame is returned  (inclusive).
        end_frame: int
            The frame below which a spike frame is returned  (exclusive).
        Returns
        ----------
        spike_train: numpy.ndarray
            An 1D array containing all the frames for each spike in the
            specified unit given the range of start and end frames.
        '''
        pass

    def set_unit_spike_features(self, unit_id, feature_name, value):
        '''This function adds a unit features data set under the given features
        name to the given unit.

        Parameters
        ----------
        unit_id: int
            The unit id for which the features will be set
        feature_name: str
            The name of the feature to be stored
        value
            The data associated with the given feature name. Could be many
            formats as specified by the user.
        '''
        if isinstance(unit_id, (int, np.integer)):
            if unit_id in self.get_unit_ids():
                if unit_id not in self._unit_features.keys():
                    self._unit_features[unit_id] = {}
                if isinstance(feature_name, str) and len(value) == len(self.get_unit_spike_train(unit_id)):
                    self._unit_features[unit_id][feature_name] = np.asarray(value)
                else:
                    if not isinstance(feature_name, str):
                        raise ValueError("feature_name must be a string")
                    else:
                        raise ValueError("feature values should have the same length as the spike train")
            else:
                raise ValueError(str(unit_id) + " is not a valid unit_id")
        else:
            raise ValueError(str(unit_id) + " must be an int")

    def get_unit_spike_features(self, unit_id, feature_name, start_frame=None, end_frame=None):
        '''This function extracts the specified spike features from the specified unit.
        It will return spike features from within three ranges:

            [start_frame, t_start+1, ..., end_frame-1]
            [start_frame, start_frame+1, ..., final_unit_spike_frame - 1]
            [0, 1, ..., end_frame-1]
            [0, 1, ..., final_unit_spike_frame - 1]

        if both start_frame and end_frame are given, if only start_frame is
        given, if only end_frame is given, or if neither start_frame or end_frame
        are given, respectively. Spike features are returned in the form of an
        array_like of spike features. In this implementation, start_frame is inclusive
        and end_frame is exclusive conforming to numpy standards.

        Parameters
        ----------
        unit_id: int
            The id that specifies a unit in the recording.
        feature_name: string
            The name of the feature to be returned.
        start_frame: int
            The frame above which a spike frame is returned  (inclusive).
        end_frame: int
            The frame below which a spike frame is returned  (exclusive).
        Returns
        ----------
        spike_features: numpy.ndarray
            An array containing all the features for each spike in the
            specified unit given the range of start and end frames.
        '''
        if isinstance(unit_id, (int, np.integer)):
            if unit_id in self.get_unit_ids():
                if unit_id not in self._unit_features.keys():
                    self._unit_features[unit_id] = {}
                if isinstance(feature_name, str):
                    if feature_name in self._unit_features[unit_id].keys():
                        if start_frame is None:
                            start_frame = 0
                        if end_frame is None:
                            end_frame = len(self.get_unit_spike_train(unit_id))
                        return self._unit_features[unit_id][feature_name][start_frame:end_frame]
                    else:
                        raise ValueError(str(feature_name) + " has not been added to unit " + str(unit_id))
                else:
                    raise ValueError(str(feature_name) + " must be a string")
            else:
                raise ValueError(str(unit_id) + " is not a valid unit_id")
        else:
            raise ValueError(str(unit_id) + " must be an int")

    def get_unit_spike_feature_names(self, unit_id=None):
        '''This function returns the names of spike features for a single
        unit or across all units (depending on the given unit_id).

        Returns
        ----------
        spike_features: list
            A list of string names for each feature in the specified unit.

        unit_id: int
            The unit_id for which the feature names will be returned. If None,
            the function will return all feature names across all units).
        '''
        if unit_id is None:
            feature_names = []
            for unit_id in self.get_unit_ids():
                curr_feature_names = self.get_unit_spike_feature_names(unit_id)
                for curr_feature_name in curr_feature_names:
                    feature_names.append(curr_feature_name)
            feature_names = sorted(list(set(feature_names)))
            return feature_names
        if isinstance(unit_id, (int, np.integer)):
            if unit_id in self.get_unit_ids():
                if unit_id not in self._unit_features:
                    self._unit_features[unit_id] = {}
                feature_names = sorted(self._unit_features[unit_id].keys())
                return feature_names
            else:
                raise ValueError(str(unit_id) + " is not a valid unit_id")
        else:
            raise ValueError(str(unit_id) + " must be an int")

    def set_unit_property(self, unit_id, property_name, value):
        '''This function adds a unit property data set under the given property
        name to the given unit.

        Parameters
        ----------
        unit_id: int
            The unit id for which the property will be set
        property_name: str
            The name of the property to be stored
        value
            The data associated with the given property name. Could be many
            formats as specified by the user.
        '''
        if isinstance(unit_id, (int, np.integer)):
            if unit_id in self.get_unit_ids():
                if unit_id not in self._unit_properties:
                    self._unit_properties[unit_id] = {}
                if isinstance(property_name, str):
                    self._unit_properties[unit_id][property_name] = value
                else:
                    raise ValueError(str(property_name) + " must be a string")
            else:
                raise ValueError(str(unit_id) + " is not a valid unit_id")
        else:
            raise ValueError(str(unit_id) + " must be an int")

    def set_units_property(self, *, unit_ids=None, property_name, values):
        '''Sets unit property data for a list of units

        Parameters
        ----------
        unit_ids: list
            The list of unit ids for which the property will be set
            Defaults to get_unit_ids()
        property_name: str
            The name of the property
        value: list
            The list of values to be set
        '''
        if unit_ids is None:
            unit_ids = self.get_unit_ids()
        for i, unit in enumerate(unit_ids):
            self.set_unit_property(unit_id=unit, property_name=property_name, value=values[i])

    def add_unit_property(self, unit_id, property_name, value):
        '''DEPRECATED! This function adds a unit property data set under the given property
        name to the given unit.

        Parameters
        ----------
        unit_id: int
            The unit id for which the property will be added
        property_name: str
            The name of the property
        value
            The data associated with the given property name. Could be many
            formats as specified by the user.
        '''
        print('WARNING: add_unit_property is deprecated. Use set_unit_property instead.')
        if isinstance(unit_id, (int, np.integer)):
            if unit_id in self.get_unit_ids():
                if isinstance(property_name, str):
                    self._unit_properties[unit_id][property_name] = value
                else:
                    raise ValueError(str(property_name) + " must be a string")
            else:
                raise ValueError(str(unit_id) + " is not a valid unit_id")
        else:
            raise ValueError(str(unit_id) + " must be an int")

    def get_unit_property(self, unit_id, property_name):
        '''This function rerturns the data stored under the property name given
        from the given unit.

        Parameters
        ----------
        unit_id: int
            The unit id for which the property will be returned
        property_name: str
            The name of the property
        Returns
        ----------
        value
            The data associated with the given property name. Could be many
            formats as specified by the user.
        '''
        if isinstance(unit_id, (int, np.integer)):
            if unit_id in self.get_unit_ids():
                if unit_id not in self._unit_properties:
                    self._unit_properties[unit_id] = {}
                if isinstance(property_name, str):
                    if property_name in list(self._unit_properties[unit_id].keys()):
                        return self._unit_properties[unit_id][property_name]
                    else:
                        raise ValueError(str(property_name) + " has not been added to unit " + str(unit_id))
                else:
                    raise ValueError(str(property_name) + " must be a string")
            else:
                raise ValueError(str(unit_id) + " is not a valid unit_id")
        else:
            raise ValueError(str(unit_id) + " must be an int")

    def get_units_property(self, *, unit_ids=None, property_name):
        '''Returns a list of values stored under the property name corresponding
        to a list of units

        Parameters
        ----------
        unit_ids: list
            The unit ids for which the property will be returned
            Defaults to get_unit_ids()
        property_name: str
            The name of the property
        Returns
        ----------
        values
            The list of values
        '''
        if unit_ids is None:
            unit_ids = self.get_unit_ids()
        values = [self.get_unit_property(unit_id=unit, property_name=property_name) for unit in unit_ids]
        return values

    def get_unit_property_names(self, unit_id=None):
        '''Get a list of property names for a given unit, or for all units if unit_id is None

        Parameters
        ----------
        unit_id: int
            The unit id for which the property names will be returned
            If None (default), will return property names for all units
        Returns
        ----------
        property_names
            The list of property names from the specified unit(s)
        '''
        if unit_id is None:
            property_names = []
            for unit_id in self.get_unit_ids():
                curr_property_names = self.get_unit_property_names(unit_id)
                for curr_property_name in curr_property_names:
                    property_names.append(curr_property_name)
            property_names = sorted(list(set(property_names)))
            return property_names
        if isinstance(unit_id, (int, np.integer)):
            if unit_id in self.get_unit_ids():
                if unit_id not in self._unit_properties:
                    self._unit_properties[unit_id] = {}
                property_names = sorted(self._unit_properties[unit_id].keys())
                return property_names
            else:
                raise ValueError(str(unit_id) + " is not a valid unit_id")
        else:
            raise ValueError(str(unit_id) + " must be an int")

    def copy_unit_properties(self, sorting, unit_ids=None):
        '''Copy unit properties from another sorting extractor to the current
        sorting extractor.

        Parameters
        ----------
        sorting: SortingExtractor
            The sorting extractor from which the properties will be copied
        unit_ids: (array_like, int)
            The list (or single value) of unit_ids for which the properties will be copied.
        '''
        if unit_ids is None:
            unit_ids = sorting.get_unit_ids()
        if isinstance(unit_ids, int):
            curr_property_names = sorting.get_unit_property_names(unit_id=unit_ids)
            for curr_property_name in curr_property_names:
                value = sorting.get_unit_property(unit_id=unit_ids, property_name=curr_property_name)
                self.set_unit_property(unit_id=unit_ids, property_name=curr_property_name, value=value)
        else:
            for unit_id in unit_ids:
                curr_property_names = sorting.get_unit_property_names(unit_id=unit_id)
                for curr_property_name in curr_property_names:
                    value = sorting.get_unit_property(unit_id=unit_id, property_name=curr_property_name)
                    self.set_unit_property(unit_id=unit_id, property_name=curr_property_name, value=value)

    def copy_unit_spike_features(self, sorting, unit_ids=None):
        '''Copy unit spike features from another sorting extractor to the current
        sorting extractor.

        Parameters
        ----------
        sorting: SortingExtractor
            The sorting extractor from which the spike features will be copied
        unit_ids: (array_like, int)
            The list (or single value) of unit_ids for which the spike features will be copied.
        def get_unit_spike_features(self, unit_id, feature_name, start_frame=None, end_frame=None):
        '''
        if unit_ids is None:
            unit_ids = sorting.get_unit_ids()
        if isinstance(unit_ids, int):
            curr_feature_names = sorting.get_unit_spike_feature_names(unit_id=unit_ids)
            for curr_feature_name in curr_feature_names:
                value = sorting.get_unit_spike_features(unit_id=unit_ids, feature_name=curr_feature_name)
                self.set_unit_spike_features(unit_id=unit_ids, feature_name=curr_feature_name, value=value)
        else:
            for unit_id in unit_ids:
                curr_feature_names = sorting.get_unit_spike_feature_names(unit_id=unit_id)
                for curr_feature_name in curr_feature_names:
                    value = sorting.get_unit_spike_features(unit_id=unit_id, feature_name=curr_feature_name)
                    self.set_unit_spike_features(unit_id=unit_id, feature_name=curr_feature_name, value=value)

    @classmethod
    def gui_params(self):
        return copy.deepcopy(self._gui_params)

    @staticmethod
    def write_sorting(sorting, save_path):
        '''This function writes out the spike sorted data file of a given sorting
        extractor to the file format of this current sorting extractor. Allows
        for easy conversion between spike sorting file formats. It is a static
        method so it can be used without instantiating this sorting extractor.

        Parameters
        ----------
        sorting: SortingExtractor
            A SortingExtractor that can extract information from the sorted data
            file to be converted to the new format.

        save_path: string
            A path to where the converted sorted data will be saved, which may
            either be a file or a folder, depending on the format.
        '''
        raise NotImplementedError("The write_sorting function is not \
                                  implemented for this extractor")
