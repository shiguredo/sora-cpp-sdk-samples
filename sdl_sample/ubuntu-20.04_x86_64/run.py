import os
import multiprocessing
import argparse
import sys
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.join(PROJECT_DIR, '..', '..')
sys.path.insert(0, BASE_DIR)


from base import (  # noqa
    cd,
    cmd,
    mkdir_p,
    add_path,
    cmake_path,
    read_version_file,
    get_webrtc_info,
    install_webrtc,
    install_llvm,
    install_boost,
    install_lyra,
    install_cmake,
    install_sdl2,
    install_sora,
    install_cli11,
)


def install_deps(source_dir, build_dir, install_dir, debug):
    with cd(BASE_DIR):
        version = read_version_file('VERSION')

        # WebRTC
        install_webrtc_args = {
            'version': version['WEBRTC_BUILD_VERSION'],
            'version_file': os.path.join(install_dir, 'webrtc.version'),
            'source_dir': source_dir,
            'install_dir': install_dir,
            'platform': 'ubuntu-20.04_x86_64',
        }
        install_webrtc(**install_webrtc_args)

        webrtc_info = get_webrtc_info(False, source_dir, build_dir, install_dir)
        webrtc_version = read_version_file(webrtc_info.version_file)

        # LLVM
        tools_url = webrtc_version['WEBRTC_SRC_TOOLS_URL']
        tools_commit = webrtc_version['WEBRTC_SRC_TOOLS_COMMIT']
        libcxx_url = webrtc_version['WEBRTC_SRC_THIRD_PARTY_LIBCXX_SRC_URL']
        libcxx_commit = webrtc_version['WEBRTC_SRC_THIRD_PARTY_LIBCXX_SRC_COMMIT']
        buildtools_url = webrtc_version['WEBRTC_SRC_BUILDTOOLS_URL']
        buildtools_commit = webrtc_version['WEBRTC_SRC_BUILDTOOLS_COMMIT']
        install_llvm_args = {
            'version':
                f'{tools_url}.{tools_commit}.'
                f'{libcxx_url}.{libcxx_commit}.'
                f'{buildtools_url}.{buildtools_commit}',
            'version_file': os.path.join(install_dir, 'llvm.version'),
            'install_dir': install_dir,
            'tools_url': tools_url,
            'tools_commit': tools_commit,
            'libcxx_url': libcxx_url,
            'libcxx_commit': libcxx_commit,
            'buildtools_url': buildtools_url,
            'buildtools_commit': buildtools_commit,
        }
        install_llvm(**install_llvm_args)

        # Boost
        install_boost_args = {
            'version': version['BOOST_VERSION'],
            'version_file': os.path.join(install_dir, 'boost.version'),
            'source_dir': source_dir,
            'install_dir': install_dir,
            'sora_version': version['SORA_CPP_SDK_VERSION'],
            'platform': 'ubuntu-20.04_x86_64',
        }
        install_boost(**install_boost_args)

        # Lyra
        install_lyra_args = {
            'version': version['LYRA_VERSION'],
            'version_file': os.path.join(install_dir, 'lyra.version'),
            'source_dir': source_dir,
            'install_dir': install_dir,
            'sora_version': version['SORA_CPP_SDK_VERSION'],
            'platform': 'ubuntu-20.04_x86_64',
        }
        install_lyra(**install_lyra_args)

        # CMake
        install_cmake_args = {
            'version': version['CMAKE_VERSION'],
            'version_file': os.path.join(install_dir, 'cmake.version'),
            'source_dir': source_dir,
            'install_dir': install_dir,
            'platform': 'linux-x86_64',
            'ext': 'tar.gz'
        }
        install_cmake(**install_cmake_args)
        add_path(os.path.join(install_dir, 'cmake', 'bin'))

        # SDL2
        install_sdl2_args = {
            'version': version['SDL2_VERSION'],
            'version_file': os.path.join(install_dir, 'sdl2.version'),
            'source_dir': source_dir,
            'build_dir': build_dir,
            'install_dir': install_dir,
            'debug': debug,
            'platform': 'linux',
            'cmake_args': [
                f"-DCMAKE_C_COMPILER={os.path.join(webrtc_info.clang_dir, 'bin', 'clang')}",
                f"-DCMAKE_CXX_COMPILER={os.path.join(webrtc_info.clang_dir, 'bin', 'clang++')}",
            ],
        }
        install_sdl2(**install_sdl2_args)

        # Sora C++ SDK
        install_sora_args = {
            'version': version['SORA_CPP_SDK_VERSION'],
            'version_file': os.path.join(install_dir, 'sora.version'),
            'source_dir': source_dir,
            'install_dir': install_dir,
            'platform': 'ubuntu-20.04_x86_64',
        }
        install_sora(**install_sora_args)

        # CLI11
        install_cli11_args = {
            'version': version['CLI11_VERSION'],
            'version_file': os.path.join(install_dir, 'cli11.version'),
            'install_dir': install_dir,
        }
        install_cli11(**install_cli11_args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action='store_true')

    args = parser.parse_args()

    configuration_dir = 'debug' if args.debug else 'release'
    dir = 'ubuntu-20.04_x86_64'
    source_dir = os.path.join(BASE_DIR, '_source', dir, configuration_dir)
    build_dir = os.path.join(BASE_DIR, '_build', dir, configuration_dir)
    install_dir = os.path.join(BASE_DIR, '_install', dir, configuration_dir)
    mkdir_p(source_dir)
    mkdir_p(build_dir)
    mkdir_p(install_dir)

    install_deps(source_dir, build_dir, install_dir, args.debug)

    configuration = 'Debug' if args.debug else 'Release'

    sample_build_dir = os.path.join(build_dir, 'sdl_sample')
    mkdir_p(sample_build_dir)
    with cd(sample_build_dir):
        webrtc_info = get_webrtc_info(False, source_dir, build_dir, install_dir)

        cmake_args = []
        cmake_args.append(f'-DCMAKE_BUILD_TYPE={configuration}')
        cmake_args.append(f"-DBOOST_ROOT={cmake_path(os.path.join(install_dir, 'boost'))}")
        cmake_args.append(f"-DLYRA_DIR={cmake_path(os.path.join(install_dir, 'lyra'))}")
        cmake_args.append(f"-DWEBRTC_INCLUDE_DIR={cmake_path(webrtc_info.webrtc_include_dir)}")
        cmake_args.append(f"-DWEBRTC_LIBRARY_DIR={cmake_path(webrtc_info.webrtc_library_dir)}")
        cmake_args.append(f"-DSORA_DIR={cmake_path(os.path.join(install_dir, 'sora'))}")
        cmake_args.append(f"-DCLI11_DIR={cmake_path(os.path.join(install_dir, 'cli11'))}")
        cmake_args.append(f"-DSDL2_DIR={cmake_path(os.path.join(install_dir, 'sdl2'))}")

        # クロスコンパイルの設定。
        # 本来は toolchain ファイルに書く内容
        cmake_args += [
            f"-DCMAKE_C_COMPILER={os.path.join(webrtc_info.clang_dir, 'bin', 'clang')}",
            f"-DCMAKE_CXX_COMPILER={os.path.join(webrtc_info.clang_dir, 'bin', 'clang++')}",
            f"-DLIBCXX_INCLUDE_DIR={cmake_path(os.path.join(webrtc_info.libcxx_dir, 'include'))}",
            '-DCMAKE_CXX_FLAGS=\'-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_EXTENSIVE\'',
        ]

        cmd(['cmake', os.path.join(PROJECT_DIR)] + cmake_args)
        cmd(['cmake', '--build', '.', f'-j{multiprocessing.cpu_count()}', '--config', configuration])


if __name__ == '__main__':
    main()
