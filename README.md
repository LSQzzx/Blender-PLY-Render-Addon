# Blender PLY Render 插件

> 📖 [English version available below](#blender-ply-render-addon)

一个用于渲染 PLY 点云文件的 Blender 插件，支持逐顶点颜色、几何节点和可选的自发光着色。

## 功能特性

- 读取 PLY 文件中的顶点颜色（`Col` 属性）并作为基础颜色使用
- 通过几何节点将网格转换为点云
- 可配置的点半径
- 可选的自发光着色及强度调节
- 兼容 Blender 3.x 和 4.x

## 环境要求

- Blender 3.0 或更高版本

## 安装方法

1. 下载 `ply_render.py`。
2. 打开 Blender，进入 **编辑 → 偏好设置 → 插件**。
3. 点击 **从磁盘安装…**，选择 `ply_render.py` 并确认。
4. 勾选 **Object: PLY Render** 旁边的复选框以启用插件。

## 使用方法

### 1. 导入 PLY 文件

进入 **文件 → 导入 → Stanford (.ply)**，导入你的点云文件。  
请确保 PLY 文件包含逐顶点颜色数据（`Col` 属性）。

### 2. 打开 PLY Render 面板

选中导入的对象，在右侧 **属性** 面板中切换到 **物体属性** 选项卡，即可看到 **PLY Render Tools** 面板。

### 3. 配置参数

| 参数 | 说明 | 默认值 |
|---|---|---|
| **点半径 (Point Radius)** | 每个渲染点的大小（场景单位） | `0.01` |
| **启用自发光 (Enable Emission)** | 为材质开启自发光 | 关闭 |
| **自发光强度 (Emission Strength)** | 启用自发光时的强度 | `0.6` |

### 4. 处理对象

点击 **处理PLY对象**。插件将：

1. 创建 `PLY_Material` 材质，将顶点颜色（`Col`）映射为基础颜色（以及可选的自发光）。
2. 添加几何节点修改器，将网格转换为具有指定半径的点云。

面板会显示当前活动对象是否已应用几何节点。

### 5. 渲染

切换为渲染模式。

## 注意事项

- 每次点击 **处理PLY对象** 都会重新构建材质和几何节点，参数修改后重新点击即可立即生效。
- 插件会在场景中添加三个属性（`ply_radius`、`ply_use_emission`、`ply_emission_strength`），这些属性会随 `.blend` 文件保存。

## 许可证

详见 [LICENSE](LICENSE)。

---

# Blender PLY Render Addon

> 📖 [中文版见上方](#blender-ply-render-插件)

A Blender addon for rendering PLY point cloud files with per-vertex color, geometry nodes, and optional emission shading.

## Features

- Reads vertex color (`Col` attribute) from imported PLY files and applies it as the base color
- Converts mesh geometry to a point cloud via Geometry Nodes
- Configurable point radius
- Optional emission shading with adjustable strength
- Compatible with Blender 3.x and 4.x

## Requirements

- Blender 3.0 or later

## Installation

1. Download `ply_render.py`.
2. Open Blender and go to **Edit → Preferences → Add-ons**.
3. Click **Install from Disk…**, select `ply_render.py`, and confirm.
4. Enable the addon by checking the box next to **Object: PLY Render**.

## Usage

### 1. Import a PLY file

Go to **File → Import → Stanford (.ply)** and import your point cloud file.  
Make sure the PLY file contains per-vertex color data (the `Col` attribute).

### 2. Open the PLY Render panel

Select the imported object, then open the **Properties** panel (right sidebar in the 3D Viewport) and navigate to the **Object Properties** tab.  
The **PLY Render Tools** panel will appear there.

### 3. Configure settings

| Setting | Description | Default |
|---|---|---|
| **Point Radius** | Size of each rendered point (in scene units) | `0.01` |
| **Enable Emission** | Toggle self-emission on the material | Off |
| **Emission Strength** | Intensity of emission when enabled | `0.6` |

### 4. Process the object

Click **Process PLY Object**. The addon will:

1. Create a `PLY_Material` that maps the vertex color (`Col`) to the base color (and optionally emission).
2. Add a Geometry Nodes modifier that converts the mesh to a point cloud with the configured radius.

The panel will indicate whether geometry nodes have been applied to the active object.

### 5. Render

Switch to render mode.

## Notes

- Re-clicking **Process PLY Object** rebuilds the material and geometry nodes from scratch, so any setting changes are applied immediately.
- The addon adds three scene-level properties (`ply_radius`, `ply_use_emission`, `ply_emission_strength`) that are saved with the `.blend` file.

## License

See [LICENSE](LICENSE).

