import SwiftUI
import RealityKit

struct ContentView: View {
    @State private var arView: ARView?
    
    var body: some View {
        ARViewContainer()
            .onAppear {
                // Initialize systems
                HRVModulator.shared.startMonitoring()
                SpatialAudioEngine.shared.start()
            }
    }
    
    struct ARViewContainer: UIViewRepresentable {
        func makeUIView(context: Context) -> ARView {
            let view = ARView(frame: .zero)
            
            // Configure AR session
            let config = ARWorldTrackingConfiguration()
            config.planeDetection = [.horizontal, .vertical]
            view.session.run(config)
            
            // Add initial anchor
            let anchor = AnchorEntity()
            view.scene.addAnchor(anchor)
            
            arView = view
            return view
        }
        
        func updateUIView(_ uiView: ARView, context: Context) {}
    }
}
