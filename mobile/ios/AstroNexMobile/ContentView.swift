import SwiftUI
import UIKit

struct ContentView: View {
    @StateObject private var viewModel = ChartViewModel()
    @State private var fullScreenChart: ChartPresentation?
    @State private var selectedChartKind: ChartKind = .radix
    @State private var selectedDataKind: DataSheetKind = .radix
    @State private var transitStep: TransitStep = .day
    @State private var transitAmount = 1
    @State private var selectedMenu: AppSection = .details
    @FocusState private var focusedField: Field?

    private enum Field {
        case name
        case country
        case location
    }

    private enum AppSection: String, CaseIterable, Identifiable {
        case details
        case people
        case data
        case transits

        var id: String { rawValue }

        var title: String {
            switch self {
            case .details: "Inicio"
            case .people: "Personas"
            case .data: "Datos"
            case .transits: "Tránsitos"
            }
        }

        var icon: String {
            switch self {
            case .details: "house"
            case .people: "person.2"
            case .data: "list.bullet.rectangle"
            case .transits: "calendar"
            }
        }
    }

    var body: some View {
        NavigationStack {
            Form {
                if selectedMenu == .details {
                Section("Datos de nacimiento") {
                    TextField("Nombre", text: $viewModel.firstName)
                        .focused($focusedField, equals: .name)
                    DatePicker("Fecha y hora", selection: $viewModel.birth, displayedComponents: [.date, .hourAndMinute])
                    if let name = viewModel.editingProfileName {
                        Text("Editando: \(name)")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                }

                Section("Lugar de nacimiento") {
                    TextField("Busca país", text: $viewModel.countryQuery)
                        .textInputAutocapitalization(.words)
                        .focused($focusedField, equals: .country)
                        .submitLabel(.search)
                        .onSubmit {
                            Task { await viewModel.searchCountries() }
                        }
                    Button("Buscar país en Astro-Nex") {
                        focusedField = nil
                        Task { await viewModel.searchCountries() }
                    }
                    .disabled(viewModel.countryQuery.trimmingCharacters(in: .whitespaces).count < 2 || viewModel.isSearchingCountries)

                    if viewModel.isSearchingCountries {
                        ProgressView("Buscando países…")
                    }
                    ForEach(viewModel.countryResults) { country in
                        Button {
                            viewModel.select(country)
                            focusedField = nil
                        } label: {
                            Text(country.name)
                        }
                    }
                    if let country = viewModel.selectedCountry {
                        LabeledContent("País seleccionado", value: country.name)
                    }

                    TextField("Busca ciudad", text: $viewModel.locationQuery)
                        .textInputAutocapitalization(.words)
                        .focused($focusedField, equals: .location)
                        .submitLabel(.search)
                        .onSubmit {
                            Task { await viewModel.searchLocations() }
                        }
                    Button("Buscar en Astro-Nex") {
                        focusedField = nil
                        Task { await viewModel.searchLocations() }
                    }
                    .disabled(viewModel.selectedCountry == nil || viewModel.locationQuery.trimmingCharacters(in: .whitespaces).count < 2 || viewModel.isSearching)

                    if viewModel.selectedCountry == nil {
                        Text("Primero busca y selecciona el país.")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }

                    if viewModel.isSearching {
                        ProgressView("Buscando localidades…")
                    }
                    ForEach(viewModel.locationResults) { location in
                        Button {
                            viewModel.select(location)
                            focusedField = nil
                            selectedMenu = .details
                        } label: {
                            VStack(alignment: .leading, spacing: 3) {
                                Text(location.city)
                                Text("\(location.region), \(location.country)")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                        }
                    }
                    if let location = viewModel.selectedLocation {
                        LabeledContent("Seleccionado", value: "\(location.city), \(location.country)")
                        LabeledContent("Zona horaria", value: location.timezone)
                    }

                    Toggle("Guardar esta persona", isOn: $viewModel.savePersonOnGenerate)
                }
                }

                if selectedMenu == .people {
                Section("Personas guardadas") {
                    if viewModel.savedProfiles.isEmpty {
                        Text("Guarda una persona para recuperar sus cartas después.")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    } else {
                        ForEach(viewModel.savedProfiles) { profile in
                            Button {
                                viewModel.load(profile)
                                focusedField = nil
                                selectedMenu = .details
                                Task { await viewModel.loadCharts() }
                            } label: {
                                VStack(alignment: .leading, spacing: 3) {
                                    Text(profile.displayName)
                                    Text("\(profile.location.city), \(profile.location.country)")
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                            }
                            .swipeActions(edge: .leading, allowsFullSwipe: false) {
                                Button("Editar") {
                                    viewModel.edit(profile)
                                    focusedField = nil
                                    selectedMenu = .details
                                }
                                .tint(.orange)
                            }
                            .swipeActions {
                                Button("Eliminar", role: .destructive) {
                                    viewModel.delete(profile)
                                }
                            }
                        }
                    }
                }
                }

                if selectedMenu == .details {
                Section {
                    Button("Generar cartas") {
                        focusedField = nil
                        Task { await viewModel.loadCharts() }
                    }
                    .frame(maxWidth: .infinity)
                    .disabled(viewModel.isLoading || viewModel.selectedLocation == nil)
                }
                }
                

                if selectedMenu == .data {
                    Section("Datos Astro-Nex") {
                        Button("Generar fichas de datos") {
                            Task { await viewModel.loadDataSheets() }
                        }
                        .disabled(viewModel.isLoadingData || viewModel.selectedLocation == nil)

                        if viewModel.isLoadingData {
                            ProgressView("Generando fichas originales…")
                        } else {
                            Picker("Ficha", selection: $selectedDataKind) {
                                ForEach(DataSheetKind.allCases) { kind in
                                    Text(kind.title).tag(kind)
                                }
                            }
                            .pickerStyle(.segmented)

                            if let image = viewModel.dataImages[selectedDataKind] {
                                Button {
                                    fullScreenChart = ChartPresentation(title: selectedDataKind.title, image: image)
                                } label: {
                                    Image(uiImage: image)
                                        .resizable()
                                        .scaledToFit()
                                        .clipShape(RoundedRectangle(cornerRadius: 12))
                                }
                                .buttonStyle(.plain)
                                Button("Ver ficha a pantalla completa") {
                                    fullScreenChart = ChartPresentation(title: selectedDataKind.title, image: image)
                                }
                                .frame(maxWidth: .infinity)
                            } else {
                                ContentUnavailableView("La ficha aparecerá aquí", systemImage: "list.bullet.rectangle")
                            }
                        }
                    }

                    Section("Ficha técnica") {
                        Button("Consultar posiciones y aspectos") {
                            Task { await viewModel.loadTechnicalDetails() }
                        }
                        .disabled(viewModel.isLoadingTechnical || viewModel.selectedLocation == nil)

                        if viewModel.isLoadingTechnical {
                            ProgressView("Leyendo datos calculados por Astro-Nex…")
                        } else if let details = viewModel.technicalDetails {
                            DisclosureGroup("Posiciones (\(details.planets.count))") {
                                ForEach(details.planets) { planet in
                                    LabeledContent(planet.displayName, value: planet.positionLabel)
                                }
                            }
                            DisclosureGroup("Aspectos (\(details.aspects.count))") {
                                ForEach(details.aspects) { aspect in
                                    VStack(alignment: .leading, spacing: 3) {
                                        Text("\(details.planetName(for: aspect.p1)) · \(aspect.displayName) · \(details.planetName(for: aspect.p2))")
                                        Text("Orbe \(aspect.orb, format: .number.precision(.fractionLength(2)))°")
                                            .font(.caption)
                                            .foregroundStyle(.secondary)
                                    }
                                }
                            }
                        } else {
                            Text("Posiciones y aspectos técnicos del motor original, sin interpretaciones.")
                                .font(.footnote)
                                .foregroundStyle(.secondary)
                        }
                    }
                }

                if selectedMenu == .transits {
                    Section("Momento actual") {
                        TextField("Busca país", text: $viewModel.momentCountryQuery)
                            .textInputAutocapitalization(.words)
                            .submitLabel(.search)
                            .onSubmit { Task { await viewModel.searchMomentCountries() } }
                        Button("Buscar país en Astro-Nex") {
                            focusedField = nil
                            Task { await viewModel.searchMomentCountries() }
                        }
                        .disabled(viewModel.momentCountryQuery.trimmingCharacters(in: .whitespaces).count < 2 || viewModel.isSearchingMomentCountries)

                        if viewModel.isSearchingMomentCountries {
                            ProgressView("Buscando países…")
                        }
                        ForEach(viewModel.momentCountryResults) { country in
                            Button(country.name) { viewModel.selectMoment(country) }
                        }
                        if let country = viewModel.momentSelectedCountry {
                            LabeledContent("País seleccionado", value: country.name)
                        }

                        TextField("Busca ciudad", text: $viewModel.momentLocationQuery)
                            .textInputAutocapitalization(.words)
                            .submitLabel(.search)
                            .onSubmit { Task { await viewModel.searchMomentLocations() } }
                        Button("Buscar en Astro-Nex") {
                            focusedField = nil
                            Task { await viewModel.searchMomentLocations() }
                        }
                        .disabled(viewModel.momentSelectedCountry == nil || viewModel.momentLocationQuery.trimmingCharacters(in: .whitespaces).count < 2 || viewModel.isSearchingMomentLocations)

                        if viewModel.isSearchingMomentLocations {
                            ProgressView("Buscando localidades…")
                        }
                        ForEach(viewModel.momentLocationResults) { location in
                            Button {
                                viewModel.selectMoment(location)
                            } label: {
                                VStack(alignment: .leading, spacing: 3) {
                                    Text(location.city)
                                    Text("\(location.region), \(location.country)")
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                            }
                        }
                        if let location = viewModel.momentLocation {
                            LabeledContent("Localidad actual", value: "\(location.city), \(location.country)")
                            LabeledContent("Zona horaria", value: location.timezone)
                        }

                        DatePicker("Fecha y hora", selection: $viewModel.transitMoment, displayedComponents: [.date, .hourAndMinute])
                        LabeledContent("Fecha activa", value: viewModel.transitMoment.formatted(date: .long, time: .shortened))
                        Picker("Avance", selection: $transitStep) {
                            ForEach(TransitStep.allCases) { step in
                                Text(step.title).tag(step)
                            }
                        }
                        .pickerStyle(.menu)

                        Stepper("Tamaño del salto: \(transitAmount)", value: $transitAmount, in: 1...365)

                        Button("Volver a ahora") {
                            resetTransitToNow()
                        }
                        .disabled(viewModel.momentLocation == nil || viewModel.isLoadingTransit)

                        HStack {
                            RepeatStepButton(
                                title: "− \(transitAmount) \(transitStep.shortTitle)",
                                action: { changeTransit(by: -transitAmount) }
                            )

                            Spacer()

                            RepeatStepButton(
                                title: "+ \(transitAmount) \(transitStep.shortTitle)",
                                prominent: true,
                                action: { changeTransit(by: transitAmount) }
                            )
                        }

                        Button {
                            Task { await viewModel.loadMoment() }
                        } label: {
                            HStack(spacing: 8) {
                                if viewModel.isLoadingTransit {
                                    ProgressView()
                                        .controlSize(.small)
                                }
                                Text("Actualizar momento")
                            }
                        }
                        .disabled(viewModel.isLoadingTransit || viewModel.momentLocation == nil)

                        if let image = viewModel.transitImage {
                            Button {
                                fullScreenChart = ChartPresentation(title: "Momento actual", image: image)
                            } label: {
                                Image(uiImage: image)
                                    .resizable()
                                    .scaledToFit()
                                    .clipShape(RoundedRectangle(cornerRadius: 12))
                                    .id(viewModel.transitRevision)
                            }
                            .buttonStyle(.plain)
                            .transition(.opacity.combined(with: .scale(scale: 0.97)))
                            .animation(.easeInOut(duration: 0.3), value: viewModel.transitRevision)
                            if let renderedMoment = viewModel.renderedTransitMoment {
                                Text("Calculada para: \(renderedMoment.formatted(date: .long, time: .shortened))")
                                    .font(.footnote)
                                    .foregroundStyle(.secondary)
                            }
                        } else {
                            ContentUnavailableView("Selecciona una localidad y una fecha", systemImage: "calendar")
                        }
                    }
                }

                if selectedMenu == .details {
                Section("Cartas Astro-Nex") {
                    if viewModel.isLoading {
                        ProgressView("Generando cartas exactas…")
                            .frame(maxWidth: .infinity)
                    } else {
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 8) {
                            ForEach(ChartKind.allCases) { kind in
                                    Button {
                                        selectedChartKind = kind
                                    } label: {
                                        Text(kind.tabTitle)
                                            .font(.subheadline.weight(.semibold))
                                            .lineLimit(1)
                                            .padding(.horizontal, 14)
                                            .padding(.vertical, 9)
                                            .foregroundStyle(selectedChartKind == kind ? Color.white : Color.primary)
                                            .background(selectedChartKind == kind ? Color.accentColor : Color(uiColor: .secondarySystemBackground))
                                            .clipShape(Capsule())
                                    }
                                    .buttonStyle(.plain)
                            }
                            }
                            .padding(.vertical, 2)
                        }

                        if let image = viewModel.chartImages[selectedChartKind] {
                            VStack(alignment: .leading, spacing: 8) {
                                Text(selectedChartKind.title)
                                    .font(.headline)
                                Button {
                                    fullScreenChart = ChartPresentation(title: selectedChartKind.title, image: image)
                                } label: {
                                    Image(uiImage: image)
                                        .resizable()
                                        .scaledToFit()
                                        .clipShape(RoundedRectangle(cornerRadius: 12))
                                }
                                .buttonStyle(.plain)
                                .accessibilityLabel("Abrir \(selectedChartKind.title) a pantalla completa")

                                Button("Ver en pantalla completa") {
                                    fullScreenChart = ChartPresentation(title: selectedChartKind.title, image: image)
                                }
                                .frame(maxWidth: .infinity)

                                Button("Ver ficha técnica") {
                                    selectedMenu = .data
                                    Task { await viewModel.loadTechnicalDetails() }
                                }
                                .frame(maxWidth: .infinity)
                            }
                        }
                        if viewModel.chartImages.isEmpty {
                            ContentUnavailableView("Tus cartas aparecerán aquí", systemImage: "moon.stars")
                        }
                    }
                }
                }
            }
            .navigationTitle("Cartas Astro-Nex")
            .alert("No se pudo generar la carta", isPresented: $viewModel.showError) {
                Button("Aceptar", role: .cancel) { }
            } message: {
                Text(viewModel.errorMessage)
            }
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Menu {
                        ForEach(AppSection.allCases) { section in
                            Button {
                                selectedMenu = section
                                focusedField = nil
                            } label: {
                                Label(section.title, systemImage: section.icon)
                            }
                        }
                    } label: {
                        Label(selectedMenu.title, systemImage: "line.3.horizontal.decrease.circle")
                    }
                }
                ToolbarItemGroup(placement: .keyboard) {
                    Spacer()
                    Button("Ocultar teclado") {
                        focusedField = nil
                    }
                }
            }
            .fullScreenCover(item: $fullScreenChart) { chart in
                FullScreenChartView(title: chart.title, image: chart.image)
            }
        }
    }

    private func changeTransit(by amount: Int) {
        guard let next = Calendar.current.date(
            byAdding: transitStep.calendarComponent,
            value: amount,
            to: viewModel.transitMoment
        ) else {
            return
        }
        viewModel.transitMoment = next
        Task { await viewModel.loadMoment() }
    }

    private func resetTransitToNow() {
        viewModel.transitMoment = Date()
        Task { await viewModel.loadMoment() }
    }
}

private struct FullScreenChartView: View {
    let title: String
    let image: UIImage
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ZoomableImageView(image: image)
                .background(Color.black)
                .ignoresSafeArea(edges: .bottom)
                .navigationTitle(title)
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .topBarLeading) {
                        Button("Cerrar") { dismiss() }
                    }
                }
        }
    }
}

private struct ChartPresentation: Identifiable {
    let id = UUID()
    let title: String
    let image: UIImage
}

enum ChartKind: String, CaseIterable, Identifiable {
    case radix = "draw_nat"
    case houses = "draw_house"
    case nodalHouses = "draw_nod"
    case soul = "draw_soul"
    case dharma = "draw_dharma"
    case nodal = "draw_ur_nodal"
    case local = "draw_local"
    case profile = "draw_prof"
    case integration = "draw_int"
    case individualClick = "draw_single"
    case radixCausal = "draw_radsoul"
    case radixDharma = "draw_raddharma"

    var id: String { rawValue }

    var title: String {
        switch self {
        case .radix: "Radix"
        case .houses: "Casas"
        case .nodalHouses: "Nodal de Casas"
        case .soul: "Causal"
        case .dharma: "Dharma"
        case .nodal: "Nodal"
        case .local: "Local"
        case .profile: "Perfil"
        case .integration: "Integración"
        case .individualClick: "Clic individual"
        case .radixCausal: "Radix-Causal"
        case .radixDharma: "Radix-Dharma"
        }
    }

    var tabTitle: String {
        switch self {
        case .radix: "Radix"
        case .houses: "Casas"
        case .nodalHouses: "Nodal Casas"
        case .soul: "Causal"
        case .dharma: "Dharma"
        case .nodal: "Nodal"
        case .local: "Local"
        case .profile: "Perfil"
        case .integration: "Integración"
        case .individualClick: "Clic individual"
        case .radixCausal: "Radix-Causal"
        case .radixDharma: "Radix-Dharma"
        }
    }
}

enum DataSheetKind: String, CaseIterable, Identifiable {
    case radix = "dat_nat"
    case houses = "dat_house"
    case nodal = "dat_nod"

    var id: String { rawValue }

    var title: String {
        switch self {
        case .radix: "Radix"
        case .houses: "Casas"
        case .nodal: "Nodal"
        }
    }
}

enum TransitStep: String, CaseIterable, Identifiable {
    case minute
    case hour
    case day
    case month
    case year

    var id: String { rawValue }

    var title: String {
        switch self {
        case .minute: "Minuto"
        case .hour: "Hora"
        case .day: "Día"
        case .month: "Mes"
        case .year: "Año"
        }
    }

    var calendarComponent: Calendar.Component {
        switch self {
        case .minute: .minute
        case .hour: .hour
        case .day: .day
        case .month: .month
        case .year: .year
        }
    }

    func label(for amount: Int) -> String {
        let unit: String
        switch self {
        case .minute: unit = amount == 1 ? "minuto" : "minutos"
        case .hour: unit = amount == 1 ? "hora" : "horas"
        case .day: unit = amount == 1 ? "día" : "días"
        case .month: unit = amount == 1 ? "mes" : "meses"
        case .year: unit = amount == 1 ? "año" : "años"
        }
        return "\(amount) \(unit)"
    }

    var shortTitle: String {
        switch self {
        case .minute: "min"
        case .hour: "h"
        case .day: "día"
        case .month: "mes"
        case .year: "año"
        }
    }
}

enum TransitViewKind: String, CaseIterable, Identifiable {
    case overlay = "draw_transits"
    case sideBySide = "rad_and_transit"

    var id: String { rawValue }

    var title: String {
        switch self {
        case .overlay: "Tránsito sobre Radix"
        case .sideBySide: "Radix y tránsito"
        }
    }
}

private struct RepeatStepButton: UIViewRepresentable {
    let title: String
    var prominent = false
    let action: () -> Void

    func makeCoordinator() -> Coordinator { Coordinator(action: action) }

    func makeUIView(context: Context) -> UIButton {
        let button = UIButton(type: .system)
        button.titleLabel?.font = .preferredFont(forTextStyle: .body)
        button.titleLabel?.adjustsFontForContentSizeCategory = true
        button.titleLabel?.adjustsFontSizeToFitWidth = true
        button.addTarget(context.coordinator, action: #selector(Coordinator.touchDown), for: .touchDown)
        button.addTarget(context.coordinator, action: #selector(Coordinator.stopRepeating), for: [.touchUpInside, .touchUpOutside, .touchCancel, .touchDragExit])
        context.coordinator.button = button
        configure(button)
        return button
    }

    func updateUIView(_ button: UIButton, context: Context) {
        context.coordinator.action = action
        configure(button)
    }

    private func configure(_ button: UIButton) {
        var configuration = UIButton.Configuration.filled()
        configuration.title = title
        configuration.cornerStyle = .capsule
        configuration.baseForegroundColor = prominent ? .white : .systemBlue
        configuration.baseBackgroundColor = prominent ? .systemBlue : .secondarySystemBackground
        configuration.contentInsets = NSDirectionalEdgeInsets(top: 9, leading: 12, bottom: 9, trailing: 12)
        button.configuration = configuration
    }

    final class Coordinator: NSObject {
        var action: () -> Void
        weak var button: UIButton?
        private var timer: Timer?

        init(action: @escaping () -> Void) {
            self.action = action
        }

        @objc func touchDown() {
            stopRepeating()
            action()
            let timer = Timer(timeInterval: 0.42, repeats: true) { [weak self] _ in
                self?.action()
            }
            self.timer = timer
            RunLoop.main.add(timer, forMode: .common)
            timer.fireDate = Date().addingTimeInterval(0.32)
            button?.isHighlighted = true
        }

        @objc func stopRepeating() {
            timer?.invalidate()
            timer = nil
            button?.isHighlighted = false
        }

        deinit { stopRepeating() }
    }
}

private struct ZoomableImageView: UIViewRepresentable {
    let image: UIImage

    func makeUIView(context: Context) -> UIScrollView {
        let scrollView = UIScrollView()
        scrollView.delegate = context.coordinator
        scrollView.minimumZoomScale = 1
        scrollView.maximumZoomScale = 6
        scrollView.zoomScale = 1
        scrollView.bouncesZoom = true
        scrollView.backgroundColor = .black
        scrollView.showsVerticalScrollIndicator = false
        scrollView.showsHorizontalScrollIndicator = false

        let imageView = UIImageView(image: image)
        imageView.contentMode = .scaleAspectFit
        imageView.isUserInteractionEnabled = true
        imageView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.addSubview(imageView)
        NSLayoutConstraint.activate([
            imageView.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor),
            imageView.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor),
            imageView.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor),
            imageView.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor),
            imageView.widthAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor),
            imageView.heightAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor)
        ])
        context.coordinator.imageView = imageView
        return scrollView
    }

    func updateUIView(_ scrollView: UIScrollView, context: Context) {
        context.coordinator.imageView?.image = image
    }

    func makeCoordinator() -> Coordinator { Coordinator() }

    final class Coordinator: NSObject, UIScrollViewDelegate {
        weak var imageView: UIImageView?

        func viewForZooming(in scrollView: UIScrollView) -> UIView? {
            imageView
        }
    }
}

@MainActor
final class ChartViewModel: ObservableObject {
    private let endpoint = URL(string: Bundle.main.object(forInfoDictionaryKey: "ASTRONEX_API_URL") as? String ?? "")!
    private let apiKey = Bundle.main.object(forInfoDictionaryKey: "ASTRONEX_API_KEY") as? String ?? ""

    @Published var firstName = ""
    @Published var birth = Date()
    @Published var countryQuery = ""
    @Published var countryResults: [AstroCountry] = []
    @Published var selectedCountry: AstroCountry?
    @Published var locationQuery = ""
    @Published var locationResults: [AstroLocation] = []
    @Published var selectedLocation: AstroLocation?
    @Published private(set) var momentLocation: AstroLocation?
    @Published var momentCountryQuery = ""
    @Published var momentCountryResults: [AstroCountry] = []
    @Published var momentSelectedCountry: AstroCountry?
    @Published var momentLocationQuery = ""
    @Published var momentLocationResults: [AstroLocation] = []
    @Published var chartImages: [ChartKind: UIImage] = [:]
    @Published var dataImages: [DataSheetKind: UIImage] = [:]
    @Published var technicalDetails: TechnicalDetails?
    @Published var transitImage: UIImage?
    @Published private(set) var transitRevision = UUID()
    @Published private(set) var renderedTransitMoment: Date?
    @Published var transitMoment = Date()
    @Published var savePersonOnGenerate = false
    @Published var isLoading = false
    @Published var isLoadingData = false
    @Published var isLoadingTechnical = false
    @Published var isLoadingTransit = false
    @Published var isSearchingCountries = false
    @Published var isSearching = false
    @Published var isSearchingMomentCountries = false
    @Published var isSearchingMomentLocations = false
    @Published var showError = false
    @Published var errorMessage = ""
    @Published private(set) var savedProfiles: [SavedProfile] = []
    @Published private(set) var editingProfileID: UUID?

    private let savedProfilesKey = "astronex.savedProfiles.v1"

    var editingProfileName: String? {
        guard let id = editingProfileID,
              let profile = savedProfiles.first(where: { $0.id == id }) else {
            return nil
        }
        return profile.displayName
    }

    var activeChartLabel: String {
        let name = firstName.trimmingCharacters(in: .whitespacesAndNewlines)
        guard let location = selectedLocation else {
            return name.isEmpty ? "Selecciona una persona" : name
        }
        return name.isEmpty ? location.city : "\(name) · \(location.city)"
    }

    init() {
        guard let data = UserDefaults.standard.data(forKey: savedProfilesKey),
              let profiles = try? JSONDecoder().decode([SavedProfile].self, from: data) else {
            return
        }
        savedProfiles = profiles
    }

    private var apiV1Endpoint: URL {
        endpoint.deletingLastPathComponent().deletingLastPathComponent()
    }

    var locationsEndpoint: URL {
        apiV1Endpoint
            .appendingPathComponent("locations")
            .appendingPathComponent("search")
    }

    var countriesEndpoint: URL {
        apiV1Endpoint
            .appendingPathComponent("locations")
            .appendingPathComponent("countries")
    }

    var technicalDetailsEndpoint: URL {
        endpoint.deletingLastPathComponent().appendingPathComponent("details")
    }

    func searchCountries() async {
        isSearchingCountries = true
        defer { isSearchingCountries = false }
        do {
            var components = URLComponents(url: countriesEndpoint, resolvingAgainstBaseURL: false)!
            components.queryItems = [URLQueryItem(name: "q", value: countryQuery)]
            var request = URLRequest(url: components.url!)
            request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
                throw URLError(.badServerResponse)
            }
            countryResults = try JSONDecoder().decode(CountrySearchResponse.self, from: data).results
            if countryResults.isEmpty {
                errorMessage = "No se encontró ese país en la base de Astro-Nex."
                showError = true
            }
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    func searchLocations() async {
        guard let country = selectedCountry else {
            errorMessage = "Primero busca y selecciona el país."
            showError = true
            return
        }
        isSearching = true
        defer { isSearching = false }
        do {
            var components = URLComponents(url: locationsEndpoint, resolvingAgainstBaseURL: false)!
            components.queryItems = [
                URLQueryItem(name: "q", value: locationQuery),
                URLQueryItem(name: "country", value: country.code),
            ]
            var request = URLRequest(url: components.url!)
            request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
                throw URLError(.badServerResponse)
            }
            locationResults = try JSONDecoder().decode(LocationSearchResponse.self, from: data).results
            if locationResults.isEmpty {
                errorMessage = "No se encontró esa ciudad en la base de localidades de Astro-Nex."
                showError = true
            }
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    func searchMomentCountries() async {
        isSearchingMomentCountries = true
        defer { isSearchingMomentCountries = false }
        do {
            var components = URLComponents(url: countriesEndpoint, resolvingAgainstBaseURL: false)!
            components.queryItems = [URLQueryItem(name: "q", value: momentCountryQuery)]
            var request = URLRequest(url: components.url!)
            request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
                throw URLError(.badServerResponse)
            }
            momentCountryResults = try JSONDecoder().decode(CountrySearchResponse.self, from: data).results
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    func searchMomentLocations() async {
        guard let country = momentSelectedCountry else { return }
        isSearchingMomentLocations = true
        defer { isSearchingMomentLocations = false }
        do {
            var components = URLComponents(url: locationsEndpoint, resolvingAgainstBaseURL: false)!
            components.queryItems = [
                URLQueryItem(name: "q", value: momentLocationQuery),
                URLQueryItem(name: "country", value: country.code),
            ]
            var request = URLRequest(url: components.url!)
            request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
                throw URLError(.badServerResponse)
            }
            momentLocationResults = try JSONDecoder().decode(LocationSearchResponse.self, from: data).results
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    func select(_ location: AstroLocation) {
        selectedLocation = location
        locationQuery = location.city
        locationResults = []
    }

    func select(_ country: AstroCountry) {
        selectedCountry = country
        countryQuery = country.name
        countryResults = []
        locationQuery = ""
        locationResults = []
        selectedLocation = nil
    }

    func selectMoment(_ country: AstroCountry) {
        momentSelectedCountry = country
        momentCountryQuery = country.name
        momentCountryResults = []
        momentLocationQuery = ""
        momentLocationResults = []
        momentLocation = nil
    }

    func selectMoment(_ location: AstroLocation) {
        momentLocation = location
        momentLocationQuery = location.city
        momentLocationResults = []
    }

    func saveCurrentProfile() {
        guard let country = selectedCountry, let location = selectedLocation else { return }
        let profile = SavedProfile(
            id: editingProfileID ?? UUID(),
            firstName: firstName.trimmingCharacters(in: .whitespacesAndNewlines),
            birth: birth,
            country: country,
            location: location
        )
        if let index = savedProfiles.firstIndex(where: { $0.id == profile.id }) {
            savedProfiles[index] = profile
        } else {
            savedProfiles.removeAll {
                $0.firstName == profile.firstName && $0.birth == profile.birth && $0.location.id == profile.location.id
            }
            savedProfiles.insert(profile, at: 0)
        }
        editingProfileID = nil
        persistProfiles()
    }

    func load(_ profile: SavedProfile) {
        populate(profile)
        editingProfileID = nil
    }

    func edit(_ profile: SavedProfile) {
        populate(profile)
        editingProfileID = profile.id
        savePersonOnGenerate = true
    }

    private func populate(_ profile: SavedProfile) {
        firstName = profile.firstName
        birth = profile.birth
        selectedCountry = profile.country
        countryQuery = profile.country.name
        countryResults = []
        selectedLocation = profile.location
        locationQuery = profile.location.city
        locationResults = []
        chartImages = [:]
    }

    func delete(_ profile: SavedProfile) {
        savedProfiles.removeAll { $0.id == profile.id }
        if editingProfileID == profile.id {
            editingProfileID = nil
        }
        persistProfiles()
    }

    private func persistProfiles() {
        guard let data = try? JSONEncoder().encode(savedProfiles) else { return }
        UserDefaults.standard.set(data, forKey: savedProfilesKey)
    }

    func loadCharts() async {
        guard selectedLocation != nil else {
            errorMessage = "Selecciona una localidad de Astro-Nex antes de generar la carta."
            showError = true
            return
        }
        isLoading = true
        defer { isLoading = false }
        do {
            if savePersonOnGenerate || editingProfileID != nil {
                saveCurrentProfile()
            }
            chartImages = [:]
            for kind in ChartKind.allCases {
                chartImages[kind] = try await renderImage(operation: kind.rawValue)
            }
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    func loadDataSheets() async {
        guard selectedLocation != nil else {
            errorMessage = "Selecciona una localidad antes de generar las fichas."
            showError = true
            return
        }
        isLoadingData = true
        defer { isLoadingData = false }
        do {
            dataImages = [:]
            for kind in DataSheetKind.allCases {
                dataImages[kind] = try await renderImage(operation: kind.rawValue)
            }
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    func loadTechnicalDetails() async {
        guard selectedLocation != nil else {
            errorMessage = "Selecciona una localidad antes de consultar los datos técnicos."
            showError = true
            return
        }
        isLoadingTechnical = true
        defer { isLoadingTechnical = false }
        do {
            var request = URLRequest(url: technicalDetailsEndpoint)
            request.cachePolicy = .reloadIgnoringLocalCacheData
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
            request.httpBody = try JSONEncoder().encode(requestPayload(operation: "draw_nat"))
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
                throw URLError(.badServerResponse)
            }
            technicalDetails = try JSONDecoder().decode(TechnicalDetails.self, from: data)
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    func loadTransit(operation: String = "draw_transits") async {
        guard selectedLocation != nil else {
            errorMessage = "Selecciona una localidad antes de calcular tránsitos."
            showError = true
            return
        }
        isLoadingTransit = true
        defer { isLoadingTransit = false }
        do {
            let requestedMoment = transitMoment
            let image = try await renderImage(
                operation: operation,
                transit: Self.localISO8601.string(from: requestedMoment)
            )
            withAnimation(.easeInOut(duration: 0.3)) {
                transitImage = image
                transitRevision = UUID()
                renderedTransitMoment = requestedMoment
            }
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    func loadMoment() async {
        guard let location = momentLocation else {
            errorMessage = "Configura la localidad actual desde Inicio antes de calcular el momento."
            showError = true
            return
        }
        isLoadingTransit = true
        defer { isLoadingTransit = false }
        do {
            let requestedMoment = transitMoment
            let image = try await renderImage(
                operation: "draw_moment",
                transit: Self.localISO8601.string(from: requestedMoment),
                location: location
            )
            withAnimation(.easeInOut(duration: 0.3)) {
                transitImage = image
                transitRevision = UUID()
                renderedTransitMoment = requestedMoment
            }
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }

    func moveTransit(by amount: Int, step: TransitStep) {
        guard let moved = Calendar.current.date(
            byAdding: step.calendarComponent,
            value: amount,
            to: transitMoment
        ) else {
            return
        }
        withAnimation(.easeInOut(duration: 0.2)) {
            transitMoment = moved
        }
    }

    private func renderImage(operation: String, transit: String? = nil, location: AstroLocation? = nil) async throws -> UIImage {
        guard location ?? selectedLocation != nil else {
            throw URLError(.badURL)
        }
        var components = URLComponents(url: endpoint, resolvingAgainstBaseURL: false)!
        components.queryItems = [URLQueryItem(name: "render", value: UUID().uuidString)]
        var request = URLRequest(url: components.url!)
        request.cachePolicy = .reloadIgnoringLocalCacheData
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        request.httpBody = try JSONEncoder().encode(requestPayload(operation: operation, transit: transit, location: location))
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200,
              let image = UIImage(data: data) else {
            throw URLError(.cannotDecodeContentData)
        }
        return image
    }

    private func requestPayload(operation: String, transit: String? = nil, location overrideLocation: AstroLocation? = nil) -> ChartRequest {
        guard let location = overrideLocation ?? selectedLocation else {
            preconditionFailure("Se requiere una localidad antes de crear una solicitud")
        }
        return ChartRequest(
            firstName: firstName,
            birth: Self.localISO8601.string(from: birth),
            timezone: location.timezone,
            latitude: location.latitude,
            longitude: location.longitude,
            city: location.city,
            region: location.region,
            country: location.country,
            operation: operation,
            transit: transit
        )
    }

    private static let localISO8601: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = .current
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
        return formatter
    }()
}

private struct ChartRequest: Encodable {
    let firstName: String
    let birth: String
    let timezone: String
    let latitude: Double
    let longitude: Double
    let city: String
    let region: String
    let country: String
    let operation: String
    let transit: String?
    let width = 1024
    let height = 1024
}

struct LocationSearchResponse: Decodable {
    let results: [AstroLocation]
}

struct CountrySearchResponse: Decodable {
    let results: [AstroCountry]
}

struct TechnicalDetails: Decodable {
    let planets: [TechnicalPlanet]
    let aspects: [TechnicalAspect]

    func planetName(for index: Int) -> String {
        planets.first(where: { $0.index == index })?.displayName ?? "Punto \(index + 1)"
    }
}

struct TechnicalPlanet: Decodable, Identifiable {
    let index: Int
    let name: String
    let longitude: Double
    let sign: String
    let degree: Double

    var id: Int { index }

    var displayName: String {
        switch name {
        case "sun": "Sol"
        case "moon": "Luna"
        case "mercury": "Mercurio"
        case "venus": "Venus"
        case "mars": "Marte"
        case "jupiter": "Júpiter"
        case "saturn": "Saturno"
        case "uranus": "Urano"
        case "neptune": "Neptuno"
        case "pluto": "Plutón"
        case "node": "Nodo"
        default: name.capitalized
        }
    }

    var positionLabel: String {
        String(format: "%.2f° %@", degree, sign.capitalized)
    }
}

struct TechnicalAspect: Decodable, Identifiable {
    let p1: Int
    let p2: Int
    let name: String
    let angle: Double
    let orb: Double
    let goodwill: Bool

    var id: String { "\(p1)-\(p2)-\(name)-\(orb)" }

    var displayName: String {
        switch name {
        case "conj": "Conjunción"
        case "semi": "Semisextil"
        case "sext": "Sextil"
        case "cuad": "Cuadratura"
        case "trig": "Trígono"
        case "quinc": "Quincuncio"
        case "opos": "Oposición"
        default: name.capitalized
        }
    }
}

struct AstroCountry: Codable, Identifiable, Equatable {
    let id: String
    let code: String
    let name: String
}

struct AstroLocation: Codable, Identifiable, Equatable {
    let id: String
    let city: String
    let region: String
    let country: String
    let timezone: String
    let latitude: Double
    let longitude: Double
}

struct SavedProfile: Codable, Identifiable, Equatable {
    let id: UUID
    let firstName: String
    let birth: Date
    let country: AstroCountry
    let location: AstroLocation

    init(id: UUID = UUID(), firstName: String, birth: Date, country: AstroCountry, location: AstroLocation) {
        self.id = id
        self.firstName = firstName
        self.birth = birth
        self.country = country
        self.location = location
    }

    var displayName: String {
        firstName.isEmpty ? "Sin nombre" : firstName
    }
}
