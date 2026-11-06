// 透過PNGのロゴマークを、余白を詰めて正方形のアイコンにする
// 使い方: make_icon 元画像.png 出力先.png サイズpx 余白率(0〜0.5) [背景色16進] [角丸率(0〜0.5)]
import AppKit

let a = CommandLine.arguments
let size = Int(a[3])!, pad = CGFloat(Double(a[4])!)
let bg: Int? = a.count > 5 ? Int(a[5], radix: 16) : nil
let radius = a.count > 6 ? CGFloat(Double(a[6])!) : 0

guard let src = NSImage(contentsOfFile: a[1]),
      let cg = src.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }

// 不透明な部分の範囲を調べる
let w = cg.width, h = cg.height
var px = [UInt8](repeating: 0, count: w * h * 4)
let ctx = CGContext(data: &px, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w * 4,
                    space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
ctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))
var minX = w, minY = h, maxX = 0, maxY = 0
for y in 0..<h { for x in 0..<w where px[(y * w + x) * 4 + 3] > 20 {
    minX = min(minX, x); maxX = max(maxX, x); minY = min(minY, y); maxY = max(maxY, y)
} }
let bw = CGFloat(maxX - minX + 1), bh = CGFloat(maxY - minY + 1)
let side = max(bw, bh) / (1 - pad * 2)
let cx = CGFloat(minX) + bw / 2, cy = CGFloat(minY) + bh / 2

let out = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: size, pixelsHigh: size, bitsPerSample: 8,
                           samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                           colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: out)
NSGraphicsContext.current!.imageInterpolation = .high
if let c = bg {
    NSColor(srgbRed: CGFloat((c >> 16) & 255) / 255, green: CGFloat((c >> 8) & 255) / 255, blue: CGFloat(c & 255) / 255, alpha: 1).setFill()
    let r = CGFloat(size) * radius
    NSBezierPath(roundedRect: NSRect(x: 0, y: 0, width: size, height: size), xRadius: r, yRadius: r).fill()
}
// 元画像の座標(下原点)で、ロゴの中心が正方形の中心に来るように描く
let k = CGFloat(size) / side
let flippedCy = CGFloat(h) - cy
NSGraphicsContext.current!.cgContext.draw(cg, in: CGRect(x: CGFloat(size) / 2 - cx * k, y: CGFloat(size) / 2 - flippedCy * k,
                                                         width: CGFloat(w) * k, height: CGFloat(h) * k))
NSGraphicsContext.restoreGraphicsState()
try! out.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[2]))
