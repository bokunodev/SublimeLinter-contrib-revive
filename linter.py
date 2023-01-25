import json
import logging

from SublimeLinter.lint import Linter, LintMatch

logger = logging.getLogger('SublimeLinter.plugin.terraform')


class Revive(Linter):
    # The executable plus all arguments used to lint. The $file_name
    # will be set by super(), and will be the folder path of the file
    # currently in the active view. The 'revive' command works
    # best on directories (modules), so it's provided here to avoid the
    # command attempting to guess what directory we are at.

    cmd = ('revive', '-formatter', 'json',
           '${project_path:${folder:${file_path}}}/...')

    # A dict of defaults for the linter’s settings.
    defaults = {'selector': 'source.go'}

    # Turn off stdin. The staticheck command requires a file.
    template_suffix = '-'

    def find_errors(self, output):
        '''
        Override find_errors() so we can parse the JSON instead
        of using a regex. revive reports errors as a steam
        of JSON object, so we parse them one line at a time.
        '''

        # Return early to stop iteration if there are no errors.
        output = output.strip()
        if not output or output == 'null':
            yield
            return

        try:
            errors = json.loads(output)
        except Exception as e:
            logger.warning(e)
            self.notify_failure()
            yield
            return

        for err in errors:
            code = 0  # revive does not have code
            error_type = err['Severity']  # warning or error
            filename = err['Position']['Start']['Filename']
            # begining of line and coll where the error occured
            line = err['Position']['Start']['Line'] - 1
            col = err['Position']['Start']['Column'] - 1
            message = err['Failure']  # error message

            # Ensure we don't set negative line/col combinations.
            if line < 0:
                line = 0
            if col < 0:
                col = 0

            yield LintMatch(
                code=code,
                filename=filename,
                line=line,
                col=col,
                error_type=error_type,
                message=message,
            )
