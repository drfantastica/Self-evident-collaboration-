import RealityKit

class GestureHandler {
    func handleTap(at position: SIMD3<Float>) {
        // Create resonance form
        let echo = EchoEntity(for: Gesture(type: .tap, position: position, velocity: 1.0))
        // Add to scene
    }

    func handleScroll(direction: SIMD3<Float>) {
        // Create interference pattern
        let scrollGesture = Gesture(type: .scroll, position: .zero, velocity: direction.length)
        let echo = EchoEntity(for: scrollGesture)
    }

    func handleLongPress(at position: SIMD3<Float>) {
        // Create note form
        let echo = EchoEntity(for: Gesture(type: .longPress, position: position, velocity: 0.5))
    }
}

struct Gesture {
    let type: GestureType
    let position: SIMD3<Float>
    let velocity: Float
}

typealias GestureType = String