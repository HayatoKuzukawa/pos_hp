// 写真をWeb用JPEGに縮小・圧縮する（使い方: convert_image 元画像 出力先 最大辺px 画質0〜1）
import AppKit
let a = CommandLine.arguments; let maxd = Double(a[3])!; let q = Double(a[4])!
let src = NSImage(contentsOfFile: a[1])!
let rep0 = src.representations[0]; let w0 = Double(rep0.pixelsWide), h0 = Double(rep0.pixelsHigh)
let s = min(1.0, maxd / max(w0,h0)); let w = Int(w0*s), h = Int(h0*s)
let rep = NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:w,pixelsHigh:h,bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
NSGraphicsContext.current!.imageInterpolation = .high
src.draw(in: NSRect(x:0,y:0,width:w,height:h)); NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using:.jpeg, properties:[.compressionFactor:q, .progressive:true])!.write(to: URL(fileURLWithPath: a[2]))
