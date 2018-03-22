import os
from conans import ConanFile, tools


class ObfuscatorLlvmInstallerConan(ConanFile):
    name = "obfuscator_llvm_installer"
    version = "4.0"
    description = 'obfuscator-llvm'
    license = "MIT"
    url = "https://github.com/theirix/conan-obfuscator_llvm_installer"
    settings = {"os": ["Linux", "Macos"], "arch": ["x86", "x86_64"]}
    build_policy = "missing"
    exports = ["LICENSE.md"]
    source_subfolder = "source_subfolder"

    def source(self):
        self.run("git clone -b llvm-%s --depth 1 https://github.com/obfuscator-llvm/obfuscator %s" % (self.version, self.source_subfolder))
        llvm_version_fixes = {'4.0' : '4.0.1'}
        if self.version in llvm_version_fixes:
            llvm_version = llvm_version_fixes[self.version]
        else:
            llvm_version = self.version
        # download additional LLVM projects
        for llvm_project in ['libcxx', 'libcxxabi']:
            name = '%s-%s.src' % (llvm_project, llvm_version)
            tools.download('https://releases.llvm.org/%s/%s.tar.xz' % (llvm_version, name), name+'.tar.xz')
            self.run('tar xJf %s.tar.xz' % name)
            # need path: llvmroot/projects/libcxx
            os.rename(name, os.path.join(self.source_subfolder, 'projects', name.replace('-%s.src' % llvm_version, '')))
        # module Obfuscation misses dependency information
        tools.save(os.path.join(self.source_subfolder, 'lib', 'Transforms', 'Obfuscation', 'LLVMBuild.txt'),
                   'required_libraries = Analysis Core Support TransformUtils',
                   append=True)

    def build(self):
        # totally isolate source folder from build, do not even make them subfolders
        tools.mkdir("build")
        with tools.chdir("build"):
            self.run("cmake " \
                     "-DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=%s " \
                     "-DLLVM_INCLUDE_TESTS=OFF -DLLVM_INCLUDE_EXAMPLES=OFF -DLLVM_TARGETS_TO_BUILD=X86 " \
                     "%s" % (self.package_folder, os.path.join(self.source_folder, self.source_subfolder)))
            self.run("make -j%s" % tools.cpu_count())
            self.run("make install")

    def package(self):
        self.copy("license*", src="sources", dst="licenses", ignore_case=True, keep_path=False)

    def package_info(self):
        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.path.append(bin_folder)
        self.env_info.CC = os.path.join(bin_folder, "clang")
        self.env_info.CXX = os.path.join(bin_folder, "clang++")
        self.env_info.SYSROOT = self.package_folder
