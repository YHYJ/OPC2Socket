# README

OPC Client在Windows系统上与OPC Server通过DCOM协议进行通信，在Linux系统需要额外安装OpenOPC组件通过OpenOPC协议进行通信

---

## Table of Contents

<!-- vim-markdown-toc GFM -->

* [环境搭建](#环境搭建)
    * [开发机环境](#开发机环境)
        * [不区分系统的依赖](#不区分系统的依赖)
        * [区分系统的依赖](#区分系统的依赖)
            * [Linux](#linux)
            * [Windows](#windows)
    * [服务器环境](#服务器环境)
        * [根据OPC Client运行的系统](#根据opc-client运行的系统)
* [OpenOPC软件](#openopc软件)
    * [OpenOPC Gateway Service](#openopc-gateway-service)
    * [opc](#opc)
* [打包成可执行文件](#打包成可执行文件)
    * [Linux](#linux-1)
    * [Windows](#windows-1)
* [issue](#issue)

<!-- vim-markdown-toc -->

---

http://openopc.sourceforge.net/

https://github.com/sightmachine/OpenOPC
https://github.com/ya-mouse/openopc
https://github.com/ya-mouse/openopc/issues/9
https://github.com/Alexhll/OpenOPC-python3.6
https://github.com/joseamaita/openopc120
https://github.com/barrybb/OpenOPC
https://github.com/jokey2k/OpenOPC

---

## 环境搭建

### 开发机环境

以下列出的依赖包需要安装到开发机用于开发

#### 不区分系统的依赖

以下是Linux/Windows都需要安装的包

1. 构建OPC Client

    - [基于Python2的OpenOPC](https://github.com/sightmachine/OpenOPC.git)
    - [基于Python3的OpenOPC](https://github.com/ya-mouse/openopc)

    根据需要安装以上两个库的其中一个

    或者Python3环境也可以使用pip安装：

    ```shell
    pip install OpenOPC-Python3x
    ```

2. 解析toml格式配置文件

    ```shell
    pip install toml
    ```

3. RPC中间件

    ```shell
    pip install Pyro4
    ```

#### 区分系统的依赖

##### Linux

无

##### Windows

1. 适用于Windows扩展的Python

    ```shell
    pip install pywin32
    ```

    或下载[pywin32.exe](https://github.com/mhammond/pywin32/releases)进行安装

### 服务器环境

以下列出的依赖包需要安装到OPC Server所在的系统

#### 根据OPC Client运行的系统

如果OPC Client运行于Windows系统则依赖包安装可以到此为止

如果是Linux系统则需要安装：

1. Python2 32bit

    注意必须是32位的Python2，这是OpenOPC Gateway Service的依赖

    > OpenOPC的README中说不依赖Python，但如果系统中没有安装Python则OpenOPC安装完成之后会提示需要安装Python，很奇怪

2. OpenOPC软件包

    因为运行于Linux系统的OPC Client无法通过DCOM协议与OPC Server通信，需要通过OpenOPC Gateway Service将数据通过OpenOPC协议代理出来

    到[sourceforge/openopc](https://sourceforge.net/projects/openopc/files/)下载最新版的OpenOPC软件包（.exe后缀）并双击安装

## OpenOPC软件

Openen软件包主要提供OpenOPC Gateway Service和`opc`命令

### OpenOPC Gateway Service

该Service安装完后会自定运行并设置为开机自启服务，这方面并不需要额外设置，但根据情况可能需要修改系统环境变量

根据OpenOPC作者barry_b的说法，在OpenOPC 1.2.0中，需要将系统环境变量**OPC_GATE_HOST**设置为希望网关服务侦听的接口的IP地址，然后重新启动网关服务以使用新设置

> In OpenOPC 1.2.0 you can solve this problem by setting system environment
> variable OPC_GATE_HOST equal to the IP address of the interface you want the Gateway Service to listen on.
> Then re-start the Gateway Service for it to pick up the new setting.
> The OPC_GATE_HOST setting was added in 1.2.0 in order to support machines that have multiple ethernet interfaces.
> By setting this you can specify which interface the Gateway Service listens on.
> But unfortunately due to an oversight on my part, the default value for OPC_GATE_HOST supplied by the installer sets it to localhost.
> Thus until you specifically set OPC_GATE_HOST your Gatetway Service will only be listening on 127.0.0.1.
> In the next release of OpenOPC I will add a new feature where you can specify OPC_GATE_HOST as "*" thus telling it to a listen on all interfaces.
> This will be the default supplied by the installer. But for now, just set it manually to be your box's IP addresses.

### opc

`opc`命令是OpenOPC软件包自带的命令行测试工具

主要测试参数有：

```shell
# 测试与OPC Server之间的DCOM连接
opc -i

# 测试OpenOPC Gateway Service是否正常运行
opc -m open -i

# 测试通过DCOM协议读取指定OPC Server的指定ITEM的值
opc -h localhost -s Matrikon.OPC.Simulation -r Random.Int4

# 测试通过OpenOPC协议读取指定OPC Server的指定ITEM的值
opc -H localhost -s Matrikon.OPC.Simulation -r Random.Int4
```

## 打包成可执行文件

> 如果需要程序脱离控制台运行，则在pyinstaller打包时在最后加一个`-w`参数即可

### Linux

打包命令如下：

```bash
pyinstaller -F opclient.py
```

### Windows

因为在Windows下使用pyinstaller进行打包需要隐式导入win32timezone，所以打包命令如下：

```bash
pyinstaller --hiddenimport win32timezone -F opclient.py
```

## issue

- 当指定的tag不存在时报错如下：

    ```python
    OpenOPC.OPCError: properties: -1073479672
    ```
