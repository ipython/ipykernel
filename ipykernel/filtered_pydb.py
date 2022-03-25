# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import pydevd

__db = pydevd.get_global_debugger()
if __db:
    __original = __db.get_file_type
    __initial = True
    def get_file_type(self, frame, abs_real_path_and_basename=None, _cache_file_type=pydevd._CACHE_FILE_TYPE):
        '''
        :param abs_real_path_and_basename:
            The result from get_abs_path_real_path_and_base_from_file or
            get_abs_path_real_path_and_base_from_frame.

        :return
            _pydevd_bundle.pydevd_dont_trace_files.PYDEV_FILE:
                If it's a file internal to the debugger which shouldn't be
                traced nor shown to the user.

            _pydevd_bundle.pydevd_dont_trace_files.LIB_FILE:
                If it's a file in a library which shouldn't be traced.

            None:
                If it's a regular user file which should be traced.
        '''
        global __initial
        if __initial:
            __initial = False
            _cache_file_type.clear()
        # Copied normalization:
        if abs_real_path_and_basename is None:
            try:
                # Make fast path faster!
                abs_real_path_and_basename = pydevd.NORM_PATHS_AND_BASE_CONTAINER[frame.f_code.co_filename]
            except:
                abs_real_path_and_basename = pydevd.get_abs_path_real_path_and_base_from_frame(frame)

        cache_key = (frame.f_code.co_firstlineno, abs_real_path_and_basename[0], frame.f_code)
        try:
            return _cache_file_type[cache_key]
        except KeyError:
            pass

        ret = __original(frame, abs_real_path_and_basename, _cache_file_type)
        if ret is self.PYDEV_FILE:
            return ret
        if not hasattr(frame, "f_locals"):
            return ret

        # if either user or lib, check with our logic
        # (we check "user" code in case any of the libs we use are in edit install)
        # logic outline:
        # - check if current frame is IPython bottom frame (if so filter it)
        # - if not, check all ancestor for ipython bottom. Filter if not present.
        # - if debugging / developing, do some sanity check of ignored frames, and log any unexecpted frames

        # do not cache, these frames might show up on different sides of the bottom frame!
        del _cache_file_type[cache_key]
        if frame.f_locals.get("__tracebackhide__") == "__ipython_bottom__":
            # Current frame is bottom frame, hide it!
            pydevd.pydev_log.debug("Ignoring IPython bottom frame: %s - %s", frame.f_code.co_filename, frame.f_code.co_name)
            ret = _cache_file_type[cache_key] = self.PYDEV_FILE
        else:
            f = frame
            while f is not None:
                if f.f_locals.get("__tracebackhide__") == "__ipython_bottom__":
                    # we found ipython bottom in stack, do not change type
                    return ret
                f = f.f_back
            pydevd.pydev_log.debug("Ignoring ipykernel frame: %s - %s", frame.f_code.co_filename, frame.f_code.co_name)

            ret = self.PYDEV_FILE
        return ret
    __db.get_file_type = get_file_type.__get__(__db, pydevd.PyDB)
    __db.is_files_filter_enabled = True
