// macOS Vision registration; no downloaded models or third-party packages.
// Build and verify: python3 .impeccable/mocks/seasons/check-alignment.py
import Foundation
import Vision
import ImageIO
import CoreGraphics
import CoreVideo
import UniformTypeIdentifiers
import simd

func image(_ path: String) throws -> CGImage {
    guard let source = CGImageSourceCreateWithURL(URL(fileURLWithPath: path) as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        throw NSError(domain: "alignment", code: 1, userInfo: [NSLocalizedDescriptionKey: "Cannot read \(path)"])
    }
    return image
}
func rgba(_ image: CGImage) -> [UInt8] {
    var bytes = [UInt8](repeating: 0, count: image.width * image.height * 4)
    bytes.withUnsafeMutableBytes { ptr in
        let context = CGContext(data: ptr.baseAddress, width: image.width, height: image.height,
                                bitsPerComponent: 8, bytesPerRow: image.width * 4,
                                space: CGColorSpace(name: CGColorSpace.sRGB)!,
                                bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
        context.draw(image, in: CGRect(x: 0, y: 0, width: image.width, height: image.height))
    }
    return bytes
}
func run() throws {
    guard CommandLine.arguments.count == 4 else {
        throw NSError(domain: "alignment", code: 2, userInfo: [NSLocalizedDescriptionKey: "Usage: align REFERENCE FLOATING OUTPUT.png"])
    }
    let reference = try image(CommandLine.arguments[1])
    let floating = try image(CommandLine.arguments[2])
    let width = reference.width, height = reference.height
    guard floating.width == width && floating.height == height else {
        throw NSError(domain: "alignment", code: 3, userInfo: [NSLocalizedDescriptionKey: "Both images must have identical dimensions"])
    }
    let request = VNGenerateOpticalFlowRequest(targetedCGImage: floating, options: [:])
    request.revision = VNGenerateOpticalFlowRequestRevision1 // Native non-ML algorithm.
    request.computationAccuracy = .veryHigh
    request.outputPixelFormat = kCVPixelFormatType_TwoComponent32Float
    try autoreleasepool {
        let handler = VNImageRequestHandler(cgImage: reference, options: [:])
        try handler.perform([request])
    }
    guard let buffer = request.results?.first?.pixelBuffer,
          CVPixelBufferGetWidth(buffer) == width, CVPixelBufferGetHeight(buffer) == height else {
        throw NSError(domain: "alignment", code: 4, userInfo: [NSLocalizedDescriptionKey: "Missing full-resolution optical flow"])
    }
    CVPixelBufferLockBaseAddress(buffer, .readOnly)
    defer { CVPixelBufferUnlockBaseAddress(buffer, .readOnly) }
    let flow = CVPixelBufferGetBaseAddress(buffer)!.assumingMemoryBound(to: Float.self)
    let stride = CVPixelBufferGetBytesPerRow(buffer) / MemoryLayout<Float>.size
    // Fit ONE affine camera correction from unchanged wall/deck texture.
    // Never apply dense seasonal flow: snow and new foliage are appearance,
    // not displacement, and would bend the roof and yard.
    let regions: [(Double, Double, Double, Double)] = [
        (0.345, 0.445, 0.44, 0.55), (0.345, 0.59, 0.44, 0.70),
        (0.23, 0.36, 0.26, 0.51), (0.09, 0.57, 0.29, 0.63),
        (0.70, 0.46, 0.72, 0.56), (0.81, 0.57, 0.83, 0.62)
    ]
    var samples: [(SIMD3<Double>, SIMD2<Double>)] = []
    for y in Swift.stride(from: 0, to: height, by: 4) {
        for x in Swift.stride(from: 0, to: width, by: 4) {
            let nx = Double(x) / Double(width), ny = Double(y) / Double(height)
            guard regions.contains(where: { nx >= $0.0 && nx <= $0.2 && ny >= $0.1 && ny <= $0.3 }) else { continue }
            let d = SIMD2<Double>(Double(flow[y * stride + x * 2]), Double(flow[y * stride + x * 2 + 1]))
            if d.x.isFinite && d.y.isFinite && simd_length(d) < Double(width) * 0.03 {
                samples.append((SIMD3<Double>(nx, ny, 1), d))
            }
        }
    }
    guard samples.count >= 50 else { throw NSError(domain: "alignment", code: 8, userInfo: [NSLocalizedDescriptionKey: "Insufficient stable architectural matches"]) }
    var retained = samples
    var cx = SIMD3<Double>.zero, cy = SIMD3<Double>.zero
    for _ in 0..<6 {
        var normal = simd_double3x3(0)
        var rx = SIMD3<Double>.zero, ry = SIMD3<Double>.zero
        for (v, d) in retained {
            normal += simd_double3x3(columns: (v * v.x, v * v.y, v * v.z))
            rx += v * d.x; ry += v * d.y
        }
        guard abs(simd_determinant(normal)) > 1e-8 else { throw NSError(domain: "alignment", code: 9) }
        cx = normal.inverse * rx; cy = normal.inverse * ry
        retained = samples.filter { v, d in simd_length(SIMD2<Double>(simd_dot(cx, v), simd_dot(cy, v)) - d) < 2.0 }
        guard retained.count >= 50 else { throw NSError(domain: "alignment", code: 10, userInfo: [NSLocalizedDescriptionKey: "Inconsistent architectural matches; manual landmarks required"]) }
    }
    let pixels = rgba(floating)
    var output = pixels
    var magnitudes = [Double]()
    for y in 0..<height {
        for x in 0..<width {
            let v = SIMD3<Double>(Double(x) / Double(width), Double(y) / Double(height), 1)
            let dx = simd_dot(cx, v)
            let dy = simd_dot(cy, v)
            guard dx.isFinite && dy.isFinite else {
                throw NSError(domain: "alignment", code: 5, userInfo: [NSLocalizedDescriptionKey: "Non-finite flow at \(x),\(y)"])
            }
            guard abs(dx) < Double(width) * 0.04 && abs(dy) < Double(height) * 0.04 else {
                throw NSError(domain: "alignment", code: 11, userInfo: [NSLocalizedDescriptionKey: "Affine correction exceeds 4% safety bound"])
            }
            let sx = min(Double(width - 1), max(0, Double(x) + dx))
            let sy = min(Double(height - 1), max(0, Double(y) + dy))
            let x0 = Int(sx), y0 = Int(sy)
            let x1 = min(width - 1, x0 + 1), y1 = min(height - 1, y0 + 1)
            let fx = sx - Double(x0), fy = sy - Double(y0)
            for channel in 0..<4 {
                let a = Double(pixels[(y0 * width + x0) * 4 + channel])
                let b = Double(pixels[(y0 * width + x1) * 4 + channel])
                let c = Double(pixels[(y1 * width + x0) * 4 + channel])
                let d = Double(pixels[(y1 * width + x1) * 4 + channel])
                let value = (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
                output[(y * width + x) * 4 + channel] = UInt8(min(255, max(0, value.rounded())))
            }
            if x % 8 == 0 && y % 8 == 0 { magnitudes.append(hypot(dx, dy)) }
        }
    }
    let out = URL(fileURLWithPath: CommandLine.arguments[3])
    guard let destination = CGImageDestinationCreateWithURL(out as CFURL, UTType.png.identifier as CFString, 1, nil) else {
        throw NSError(domain: "alignment", code: 6, userInfo: [NSLocalizedDescriptionKey: "Cannot create output"])
    }
    output.withUnsafeMutableBytes { ptr in
        let context = CGContext(data: ptr.baseAddress, width: width, height: height, bitsPerComponent: 8,
                                bytesPerRow: width * 4, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                                bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
        CGImageDestinationAddImage(destination, context.makeImage()!, nil)
    }
    guard CGImageDestinationFinalize(destination) else { throw NSError(domain: "alignment", code: 7) }
    magnitudes.sort()
    let stats: [String: Any] = ["width": width, "height": height, "algorithm": "Robust affine fit to native Vision revision-1 flow on stable architectural texture; no dense warp", "median_displacement_px": magnitudes[magnitudes.count / 2], "p95_displacement_px": magnitudes[Int(Double(magnitudes.count - 1) * 0.95)], "matches": samples.count, "inliers": retained.count, "dx_normalized_xy1": [cx.x, cx.y, cx.z], "dy_normalized_xy1": [cy.x, cy.y, cy.z]]
    let json = try JSONSerialization.data(withJSONObject: stats, options: [.prettyPrinted, .sortedKeys])
    try json.write(to: URL(fileURLWithPath: out.path + ".json"))
    print(String(data: json, encoding: .utf8)!)
}
do { try run() } catch { fputs("\(error.localizedDescription)\n", stderr); exit(1) }
