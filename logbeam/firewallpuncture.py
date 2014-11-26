import subprocess
import logging
import atexit


class FirewallPuncture:
    def __init__(self, port, portRange):
        self._port = port
        self._portRange = portRange
        self._punctured = False
        if not self._canSudo():
            raise Exception("User not allowed to sudo - can not verify firewall enables access to logbeam")
        if not self._firewallHasRejectRule():
            logging.debug("No need to puncture firewall - its down")
            return
        self._punctureFirewall()
        atexit.register(self.undo)

    def undo(self):
        if not self._punctured:
            return
        self._punctured = False
        try:
            self._run(["iptables", "-D", "INPUT", "-p", "tcp", "--dport", str(self._port), "-j", "ACCEPT"])
        except:
            self._run(self._delPortRangeCmd(), raiseOnError=False)
            raise
        self._run([
            "iptables", "-D", "INPUT", "-p", "tcp", "--match", "multiport",
            "--dports", "%s:%s" % self._portRange, "-j", "ACCEPT"])

    def _delPortRangeCmd(self):
        return [
            "iptables", "-D", "INPUT", "-p", "tcp", "--match", "multiport",
            "--dports", "%s:%s" % self._portRange, "-j", "ACCEPT"]

    def _punctureFirewall(self):
        self._run([
            "iptables", "-I", "INPUT", "-p", "tcp", "--match", "multiport",
            "--dports", "%s:%s" % self._portRange, "-j", "ACCEPT"])
        try:
            self._run(["iptables", "-I", "INPUT", "-p", "tcp", "--dport", str(self._port), "-j", "ACCEPT"])
        except:
            self._run(self._delPortRangeCmd(), raiseOnError=False)
            raise
        self._punctured = True

    def _canSudo(self):
        return self._run(["echo"], raiseOnError=False) is not None

    def _firewallHasRejectRule(self):
        output = self._run(["iptables", "--list", "INPUT"])
        return 'REJECT' in output

    def _run(self, cmd, raiseOnError=True):
        fullCmd = ["sudo", "-n"] + cmd
        try:
            output = subprocess.check_output(fullCmd, close_fds=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if raiseOnError:
                raise Exception("Cmd '%s' failed, output:\n%s" % (fullCmd, e.output))
            else:
                return None
        return output
