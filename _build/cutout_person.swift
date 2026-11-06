// 写真から人物だけを切り抜いて背景透過PNGにする（macOS標準の人物認識 Vision を使用）
// 使い方: cutout_person 元画像 出力先.png 横幅px
import AppKit
import CoreImage
import Vision

let a = CommandLine.arguments
let src = URL(fileURLWithPath: a[1]), out = URL(fileURLWithPath: a[2])
let maxW = CGFloat(Double(a[3])!)

guard let input = CIImage(contentsOf: src, options: [.applyOrientationProperty: true]) else { exit(1) }
// 手元のSDKが古くクラス名で直接書けないため、OS本体（macOS 12以降）の機能を実行時に呼び出す
guard let cls = NSClassFromString("VNGeneratePersonSegmentationRequest") as? VNRequest.Type else { exit(3) }
let req = cls.init()
req.setValue(0, forKey: "qualityLevel") // 0 = accurate
req.setValue(kCVPixelFormatType_OneComponent8, forKey: "outputPixelFormat")
try! VNImageRequestHandler(ciImage: input, options: [:]).perform([req])
guard let maskBuf = (req.results?.first as? VNPixelBufferObservation)?.pixelBuffer else { exit(2) }

// マスクを元画像サイズに拡大し、輪郭をわずかにぼかして自然になじませる
var mask = CIImage(cvPixelBuffer: maskBuf)
mask = mask.transformed(by: CGAffineTransform(scaleX: input.extent.width / mask.extent.width,
                                              y: input.extent.height / mask.extent.height))
mask = mask.applyingGaussianBlur(sigma: 1.2).cropped(to: input.extent)

let clear = CIImage(color: .clear).cropped(to: input.extent)
let cut = input.applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: clear, kCIInputMaskImageKey: mask])

// 人物のある範囲だけを切り出す
let ctx = CIContext()
let maskCG = ctx.createCGImage(mask, from: input.extent)!
let mw = maskCG.width, mh = maskCG.height
var data = [UInt8](repeating: 0, count: mw * mh)
let gray = CGContext(data: &data, width: mw, height: mh, bitsPerComponent: 8, bytesPerRow: mw,
                     space: CGColorSpaceCreateDeviceGray(), bitmapInfo: 0)!
gray.draw(maskCG, in: CGRect(x: 0, y: 0, width: mw, height: mh))
var minX = mw, minY = mh, maxX = 0, maxY = 0
for y in 0..<mh { for x in 0..<mw where data[y * mw + x] > 40 {
    minX = min(minX, x); maxX = max(maxX, x); minY = min(minY, y); maxY = max(maxY, y)
} }
// CGContext は下原点なので、上下を反転して CIImage 座標に合わせる
let box = CGRect(x: CGFloat(minX), y: CGFloat(mh - 1 - maxY), width: CGFloat(maxX - minX + 1), height: CGFloat(maxY - minY + 1))
    .insetBy(dx: -4, dy: -4).intersection(input.extent)

let scale = min(1, maxW / box.width)
let final = cut.cropped(to: box).transformed(by: CGAffineTransform(translationX: -box.minX, y: -box.minY))
    .transformed(by: CGAffineTransform(scaleX: scale, y: scale))
let cg = ctx.createCGImage(final, from: final.extent, format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)!
let rep = NSBitmapImageRep(cgImage: cg)
try! rep.representation(using: .png, properties: [:])!.write(to: out)
print("\(cg.width)x\(cg.height)")
