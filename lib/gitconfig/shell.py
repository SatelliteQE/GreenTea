from subprocess import PIPE, STDOUT, Popen


def shell(command):
    process = Popen(command, stdout=PIPE, stdin=PIPE,
                    stderr=STDOUT, shell=True)
    r = process.communicate()
    if process.returncode != 0:
        raise SystemError(r[0])
    else:
        # remove line break
        return "\n".join(r[0].splitlines())
