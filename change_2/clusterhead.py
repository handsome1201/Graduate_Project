import vehicle
class PublicTransportation:
    def __init__(self, fog_mips, fog_core, fog_ram, fog_cpu_util, veh, clu_mem):
        self.fog_mips=fog_mips
        self.fog_core=fog_core
        self.fog_ram=fog_ram
        self.fog_cpu_util=fog_cpu_util
        self.veh=veh
        self.clu_mem=clu_mem

    #define setter and getter
    def get_fog_mips(self):
        return self.fog_mips

    def set_fog_mips(self, fog_mips):
        self.fog_mips=fog_mips

    def get_fog_core(self):
        return self.fog_core

    def set_fog_core(self, fog_core):
        self.fog_core=fog_core

    def get_fog_ram(self):
        return self.fog_ram

    def set_fog_ram(self, fog_ram):
        self.fog_ram=fog_ram

    def get_fog_cpu_util(self):
        return self.fog_cpu_util

    def set_fog_cpu_util(self, fog_cpu_util):
        self.fog_cpu_util=fog_cpu_util

    def get_veh(self):
        return self.veh

    def set_veh(self, veh):
        self.veh=veh
    
    def get_clu_mem(self):
        return self.clu_mem

    def set_clu_mem(self, clu_mem):
        self.clu_mem=clu_mem
    
    def select_cluster_member():
        pass
        