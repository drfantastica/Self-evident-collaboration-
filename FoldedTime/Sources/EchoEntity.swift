import RealityKit

class EchoEntity: Entity, HasPhysics, HasTransform {
    static var decayRate: Float = 0.1

    convenience init(for gesture: Gesture) {
        self.init()
        
        // Create geometric form based on gesture type
        let mesh = MeshResource.generateBox(size: 0.1)
        let material = SimpleMaterial(color: .white, isMetallic: true)
        
        let form = ModelEntity(mesh: mesh, materials: [material])
        form.position = gesture.position
        
        // Velocity-based persistence
        let velocity = gesture.velocity
        let persistence = 30 - (velocity * 0.5) // 15-30s range
        
        form.addComponent(
            TimerComponent(
                .init(
                    .after(persistence) {
                        form.removeFromParent()
                    }
                )
            )
        )
        
        // Add to scene
        self.children.append(form)
    }
}
