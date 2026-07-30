import SwiftUI

@main
struct AstroNexMobileApp: App {
    @State private var showsSplash = true

    var body: some Scene {
        WindowGroup {
            Group {
                if showsSplash {
                    AstroNexSplashView()
                } else {
                    ContentView()
                }
            }
            .task {
                try? await Task.sleep(nanoseconds: 1_000_000_000)
                withAnimation(.easeOut(duration: 0.2)) {
                    showsSplash = false
                }
            }
        }
    }
}

private struct AstroNexSplashView: View {
    var body: some View {
        Color.black
            .overlay {
                Image("AstroNexSplash")
                    .resizable()
                    .scaledToFit()
                    .padding(24)
            }
            .ignoresSafeArea()
    }
}
