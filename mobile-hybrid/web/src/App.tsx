import { useState, useEffect, useRef } from 'react';
import natalInput from './natal_input.json';

import { ChartSvg } from './components/chart/ChartSvg';
import { generateChartSvg } from './components/chart/AstroChartGenerator';
import { ChartCanvas } from './components/chart/ChartCanvas';
import { initDatabase, searchCountries, searchLocations } from './DatabaseService';

import {
  NavigationBar,
  Form,
  Section,
  FormRow,
  LabeledContent,
  TextField,
  Toggle,
  SegmentedControl,
  DisclosureGroup,
  Stepper,
  SwipeableRow,
  KonstaAppWrapper,
  Button
} from './components/ui/iOS';

const parsedInput = natalInput as any;

function App() {
  const [selectedMenu, setSelectedMenu] = useState<'details' | 'people' | 'data' | 'transits'>('details');
  const [status, setStatus] = useState<string>('Esperando acción...');

  // Radix Chart Data
  const [chartData, setChartData] = useState<any>(null);
  useEffect(() => { handleCalculate(false); }, []);
  const [chartLoading, setChartLoading] = useState(false);
  const [useCanvas, setUseCanvas] = useState(true);

  // Selected Chart Type
  const [selectedChartType, setSelectedChartType] = useState<string>('draw_nat');
  const chartTypes = [
    { id: 'draw_nat', label: 'Radix' },
    { id: 'draw_house', label: 'Casas' },
    { id: 'draw_nod', label: 'Nodal Casas' },
    { id: 'draw_soul', label: 'Causal' },
    { id: 'draw_dharma', label: 'Dharma' },
    { id: 'draw_ur_nodal', label: 'Nodal' },
    { id: 'draw_local', label: 'Local' }
  ];

  // Form State
  const [name, setName] = useState(`${parsedInput.firstName} ${parsedInput.lastName}`);
  const [date, setDate] = useState(parsedInput.birth.slice(0, 10));
  const [time, setTime] = useState(parsedInput.birth.slice(11, 16));
  const [timezone] = useState(parsedInput.timezone || 'America/Bogota');

  const [countryQuery, setCountryQuery] = useState(parsedInput.country);
  const [countryCode, setCountryCode] = useState('CO');
  const [countries, setCountries] = useState<any[]>([]);

  const [locationQuery, setLocationQuery] = useState(parsedInput.city);
  const [locations, setLocations] = useState<any[]>([]);

  const [lat, setLat] = useState(parsedInput.latitude);
  const [lon, setLon] = useState(parsedInput.longitude);

  const [savePerson, setSavePerson] = useState(false);
  const [savedProfiles, setSavedProfiles] = useState<any[]>([]);

  const workerRef = useRef<Worker | null>(null);

  useEffect(() => {
    initDatabase();
    const profiles = localStorage.getItem('astronex_profiles');
    if (profiles) setSavedProfiles(JSON.parse(profiles));

    workerRef.current = new Worker(new URL('./engine.worker.ts', import.meta.url), { type: 'module' });
    workerRef.current.onmessage = (e) => {
      const data = e.data;
      if (data.type === 'SUCCESS') {
        setStatus('✅ Carta Calculada');
        setChartData(data.chartData);
        setChartLoading(false);
      } else if (data.type === 'ERROR') {
        setStatus(`❌ Error: ${data.message}`);
        setChartLoading(false);
      }
    };
    return () => workerRef.current?.terminate();
  }, []);

  // Transit Data
  const [transitDate, setTransitDate] = useState('2026-07-29');
  const [transitTime, setTransitTime] = useState('12:00');
  const [transitStep, setTransitStep] = useState('day');
  const [transitAmount, setTransitAmount] = useState(1);
  const transitMomentRef = useRef(new Date('2026-07-29T12:00:00Z'));
  const transitRepeatDelayRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const transitRepeatRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    transitMomentRef.current = new Date(`${transitDate}T${transitTime}:00Z`);
  }, [transitDate, transitTime]);

  useEffect(() => () => {
    if (transitRepeatDelayRef.current) clearTimeout(transitRepeatDelayRef.current);
    if (transitRepeatRef.current) clearInterval(transitRepeatRef.current);
  }, []);

  useEffect(() => {
    if (countryQuery.length >= 2 && !countries.find(c => c.name === countryQuery)) {
      searchCountries(countryQuery).then(res => setCountries(res));
    } else {
      setCountries([]);
    }
  }, [countryQuery]);

  useEffect(() => {
    if (locationQuery.length >= 2 && !locations.find(l => l.city === locationQuery)) {
      searchLocations(locationQuery, countryCode).then(res => setLocations(res));
    } else {
      setLocations([]);
    }
  }, [locationQuery, countryCode]);

  const handleCalculate = (isTransit = false) => {
    setStatus('Calculando posiciones...');
    setChartLoading(true);

    const [year, month, day] = date.split('-').map(Number);
    const [hourStr, minStr] = time.split(':');
    const hour = Number(hourStr) + (Number(minStr) / 60);

    let calcYear = year, calcMonth = month, calcDay = day, calcHour = hour;

    if (isTransit) {
      const d = transitMomentRef.current;
      calcYear = d.getUTCFullYear();
      calcMonth = d.getUTCMonth() + 1;
      calcDay = d.getUTCDate();
      calcHour = d.getUTCHours() + (d.getUTCMinutes() / 60);
    }

    workerRef.current?.postMessage({
      type: 'CALCULATE',
      year: calcYear,
      month: calcMonth,
      day: calcDay,
      hour: calcHour,
      lat: Number(lat),
      lon: Number(lon),
      timezone,
      chartType: selectedChartType
    });

    if (savePerson) handleSaveProfile();
  };

  useEffect(() => {
    if (chartData && !chartLoading) {
      handleCalculate(selectedMenu === 'transits');
    }
  }, [selectedChartType]);

  const handleSaveProfile = () => {
    const profile = { id: Date.now(), name, date, time, lat, lon, countryQuery, locationQuery, countryCode };
    const newProfiles = [...savedProfiles, profile];
    setSavedProfiles(newProfiles);
    localStorage.setItem('astronex_profiles', JSON.stringify(newProfiles));
    setSavePerson(false);
  };

  const loadProfile = (p: any) => {
    setName(p.name);
    setDate(p.date);
    setTime(p.time);
    setLat(p.lat);
    setLon(p.lon);
    setCountryQuery(p.countryQuery);
    setLocationQuery(p.locationQuery);
    setCountryCode(p.countryCode);
    setSelectedMenu('details');
    setTimeout(() => handleCalculate(), 100);
  };

  const handleDeleteProfile = (id: number) => {
    const newProfiles = savedProfiles.filter(p => p.id !== id);
    setSavedProfiles(newProfiles);
    localStorage.setItem('astronex_profiles', JSON.stringify(newProfiles));
  };

  const changeTransit = (direction: 1 | -1) => {
    const d = new Date(transitMomentRef.current);
    const amount = transitAmount * direction;

    if (transitStep === 'day') {
      d.setUTCDate(d.getUTCDate() + amount);
    } else if (transitStep === 'hour') {
      d.setUTCHours(d.getUTCHours() + amount);
    } else if (transitStep === 'minute') {
      d.setUTCMinutes(d.getUTCMinutes() + amount);
    } else if (transitStep === 'month') {
      const targetMonth = d.getUTCMonth() + amount;
      const expectedMonth = ((targetMonth % 12) + 12) % 12;
      d.setUTCMonth(targetMonth);
      if (d.getUTCMonth() !== expectedMonth) d.setUTCDate(0);
    } else if (transitStep === 'year') {
      const targetYear = d.getUTCFullYear() + amount;
      const expectedMonth = d.getUTCMonth();
      d.setUTCFullYear(targetYear);
      if (d.getUTCMonth() !== expectedMonth) d.setUTCDate(0);
    }

    setTransitDate(d.toISOString().split('T')[0]);
    setTransitTime(d.toISOString().split('T')[1].slice(0, 5));
    transitMomentRef.current = d;
    handleCalculate(true);
  };

  const clearTransitRepeat = () => {
    if (transitRepeatDelayRef.current) clearTimeout(transitRepeatDelayRef.current);
    if (transitRepeatRef.current) clearInterval(transitRepeatRef.current);
    transitRepeatDelayRef.current = null;
    transitRepeatRef.current = null;
  };

  const stopTransitRepeat = () => {
    clearTransitRepeat();
  };

  const startTransitRepeat = (direction: 1 | -1) => {
    clearTransitRepeat();
    changeTransit(direction);
    transitRepeatDelayRef.current = setTimeout(() => {
      transitRepeatRef.current = setInterval(() => changeTransit(direction), 150);
    }, 350);
  };

  const chartSize = Math.min(window.innerWidth - 40, 500);

  return (
    <KonstaAppWrapper>
      <NavigationBar
        title="Cartas Astro-Nex"
        selectedMenu={selectedMenu}
        onSelectMenu={(id) => setSelectedMenu(id as any)}
        menuOptions={[
          { id: 'details', label: 'Inicio', icon: '' },
          { id: 'people', label: 'Personas', icon: '' },
          { id: 'data', label: 'Datos', icon: '' },
          { id: 'transits', label: 'Tránsitos', icon: '' }
        ]}
      />

      <Form>
        {selectedMenu === 'details' && (
          <>
            <Section title="Datos de nacimiento">
              <TextField placeholder="Nombre" value={name} onChange={setName} />
              <FormRow>
                <span className="ios-label">Fecha y hora</span>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input type="date" value={date} onChange={e => setDate(e.target.value)} className="ios-input" style={{ width: '130px', textAlign: 'right', padding: '6px', background: '#3a3a3c', borderRadius: '6px' }} />
                  <input type="time" value={time} onChange={e => setTime(e.target.value)} className="ios-input" style={{ width: '80px', textAlign: 'right', padding: '6px', background: '#3a3a3c', borderRadius: '6px' }} />
                </div>
              </FormRow>
            </Section>

            <Section title="Lugar de nacimiento">
              <FormRow style={{ flexDirection: 'column', alignItems: 'stretch' }}>
                <div style={{ position: 'relative' }}>
                  <input type="text" className="ios-input" value={countryQuery} onChange={e => setCountryQuery(e.target.value)} placeholder="Busca país" style={{ textAlign: 'left', padding: '6px 0' }} />
                  {countries.length > 0 && (
                    <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, background: '#2c2c2e', zIndex: 10, borderRadius: '8px', overflow: 'hidden' }}>
                      {countries.map(c => (
                        <div key={c.id} style={{ padding: '12px', borderBottom: '1px solid #38383a' }} onClick={() => { setCountryQuery(c.name); setCountryCode(c.code); setCountries([]); }}>
                          {c.name}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </FormRow>
              <LabeledContent label="País seleccionado" value={countryCode} />

              <FormRow style={{ flexDirection: 'column', alignItems: 'stretch' }}>
                <div style={{ position: 'relative' }}>
                  <input type="text" className="ios-input" value={locationQuery} onChange={e => setLocationQuery(e.target.value)} placeholder="Busca ciudad" style={{ textAlign: 'left', padding: '6px 0' }} />
                  {locations.length > 0 && (
                    <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, background: '#2c2c2e', zIndex: 10, borderRadius: '8px', overflow: 'hidden' }}>
                      {locations.map(l => (
                        <div key={l.id} style={{ padding: '12px', borderBottom: '1px solid #38383a' }} onClick={() => { setLocationQuery(l.city); setLat(l.latitude); setLon(l.longitude); setLocations([]); }}>
                          {l.city}, {l.region}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </FormRow>
              <LabeledContent label="Seleccionado" value={`${locationQuery}, ${countryCode}`} />
              <Toggle label="Guardar esta persona" checked={savePerson} onChange={setSavePerson} />
            </Section>

            <Section>
              <FormRow>
                <Button onClick={() => handleCalculate(false)}>
                  {chartLoading ? 'Generando...' : 'Generar cartas'}
                </Button>
              </FormRow>
              {status !== 'Esperando acción...' && (
                <div style={{ textAlign: 'center', color: 'var(--ios-secondary)', fontSize: '13px', margin: '8px 0' }}>
                  {status}
                </div>
              )}
            </Section>

            {chartData && (
              <Section title="Cartas Astro-Nex">
                <div className="ios-capsule-scroll">
                  {chartTypes.map(ct => (
                    <div
                      key={ct.id}
                      className={`ios-capsule ${selectedChartType === ct.id ? 'active' : ''}`}
                      onClick={() => setSelectedChartType(ct.id)}
                    >
                      {ct.label}
                    </div>
                  ))}
                </div>

                <div style={{ display: 'flex', justifyContent: 'center', marginTop: '16px' }}>
                  <Toggle label="Modo Canvas (Prueba)" checked={useCanvas} onChange={setUseCanvas} />
                </div>

                <div style={{ display: 'flex', justifyContent: 'center', marginTop: '16px', marginBottom: '16px' }}>
                  <div style={{ width: chartSize, height: chartSize, backgroundColor: '#fff', borderRadius: '12px', padding: '10px' }}>
                    {useCanvas ? (
                      <ChartCanvas width={chartSize} height={chartSize} chartData={chartData} />
                    ) : (
                      <ChartSvg
                        width={chartSize}
                        height={chartSize}
                        svgContent={generateChartSvg(chartData, { width: chartSize, height: chartSize, isTransit: false })}
                      />
                    )}
                  </div>
                </div>

                <FormRow>
                  <Button onClick={() => setSelectedMenu('data')}>Ver ficha técnica</Button>
                </FormRow>
              </Section>
            )}
          </>
        )}

        {selectedMenu === 'people' && (
          <Section title="Personas guardadas">
            {savedProfiles.length === 0 ? (
              <FormRow><span style={{ color: 'var(--ios-secondary)' }}>Guarda una persona para recuperar sus cartas.</span></FormRow>
            ) : (
              savedProfiles.map(p => (
                <SwipeableRow key={p.id} onEdit={() => loadProfile(p)} onDelete={() => handleDeleteProfile(p.id)}>
                  <div style={{ display: 'flex', flexDirection: 'column' }} onClick={() => loadProfile(p)}>
                    <span style={{ fontSize: '17px', color: 'var(--ios-text)' }}>{p.name}</span>
                    <span style={{ fontSize: '13px', color: 'var(--ios-secondary)' }}>{p.locationQuery}, {p.countryCode}</span>
                  </div>
                </SwipeableRow>
              ))
            )}
          </Section>
        )}

        {selectedMenu === 'data' && (
          <>
            <Section title="Datos Astro-Nex">
              <SegmentedControl
                options={[{ id: 'radix', label: 'Radix' }, { id: 'casas', label: 'Casas' }, { id: 'nodal', label: 'Nodal' }]}
                selected="radix"
                onChange={() => { }}
              />
              <div style={{ textAlign: 'center', color: 'var(--ios-secondary)', padding: '20px' }}>Ficha técnica seleccionada</div>
            </Section>

            <Section title="Ficha técnica">
              {chartData ? (
                <>
                  <DisclosureGroup title={`Dignidades (${chartData.dynamics?.signs?.elem ? 'Calculadas' : 'No disp.'})`}>
                    {chartData.dynamics && (
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', fontSize: '15px' }}>
                        <div>
                          <div style={{ color: 'var(--ios-secondary)' }}>Fuego: {chartData.dynamics.signs.elem.fire}</div>
                          <div style={{ color: 'var(--ios-secondary)' }}>Tierra: {chartData.dynamics.signs.elem.earth}</div>
                          <div style={{ color: 'var(--ios-secondary)' }}>Aire: {chartData.dynamics.signs.elem.air}</div>
                          <div style={{ color: 'var(--ios-secondary)' }}>Agua: {chartData.dynamics.signs.elem.water}</div>
                        </div>
                        <div>
                          <div style={{ color: 'var(--ios-secondary)' }}>Cardinal: {chartData.dynamics.signs.cross.card}</div>
                          <div style={{ color: 'var(--ios-secondary)' }}>Fijo: {chartData.dynamics.signs.cross.fix}</div>
                          <div style={{ color: 'var(--ios-secondary)' }}>Mutable: {chartData.dynamics.signs.cross.mut}</div>
                        </div>
                      </div>
                    )}
                  </DisclosureGroup>
                  <DisclosureGroup title={`Posiciones (${chartData.planets.length})`}>
                    <div style={{ fontSize: '15px', color: 'var(--ios-secondary)' }}>
                      {chartData.planets.map((p: any) => (
                        <div key={p.name} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
                          <span style={{ textTransform: 'capitalize' }}>{p.name}</span>
                          <span>{Math.floor(p.degree)}° {(p.degree % 1 * 60).toFixed(0)}' {p.sign}</span>
                        </div>
                      ))}
                    </div>
                  </DisclosureGroup>
                </>
              ) : (
                <FormRow><span style={{ color: 'var(--ios-secondary)' }}>Calcula una carta primero.</span></FormRow>
              )}
            </Section>
          </>
        )}

        {selectedMenu === 'transits' && (
          <>
            <Section title="Momento actual">
              <FormRow>
                <span className="ios-label">Fecha y hora</span>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input type="date" value={transitDate} onChange={e => {
                    const val = e.target.value;
                    setTransitDate(val);
                    transitMomentRef.current = new Date(`${val}T${transitTime}:00Z`);
                    handleCalculate(true);
                  }} className="ios-input" style={{ width: '130px', textAlign: 'right', padding: '6px', background: '#3a3a3c', borderRadius: '6px' }} />
                  <input type="time" value={transitTime} onChange={e => {
                    const val = e.target.value;
                    setTransitTime(val);
                    transitMomentRef.current = new Date(`${transitDate}T${val}:00Z`);
                    handleCalculate(true);
                  }} className="ios-input" style={{ width: '80px', textAlign: 'right', padding: '6px', background: '#3a3a3c', borderRadius: '6px' }} />
                </div>
              </FormRow>
              <SegmentedControl
                options={[
                  { id: 'minute', label: 'Min' },
                  { id: 'hour', label: 'Hora' },
                  { id: 'day', label: 'Día' },
                  { id: 'month', label: 'Mes' },
                  { id: 'year', label: 'Año' }
                ]}
                selected={transitStep}
                onChange={setTransitStep}
              />
              <Stepper label={`Salto: ${transitAmount}`} value={transitAmount} onChange={setTransitAmount} />
              <div className="offline-transit-actions">
                <Button className="offline-secondary-button transit-repeat-button" onPointerDown={(event) => { event.preventDefault(); event.currentTarget.setPointerCapture(event.pointerId); startTransitRepeat(-1); }} onPointerUp={stopTransitRepeat} onPointerCancel={stopTransitRepeat} onPointerLeave={stopTransitRepeat} onClick={(event) => event.preventDefault()}>− Salto</Button>
                <Button className="offline-secondary-button transit-repeat-button" onPointerDown={(event) => { event.preventDefault(); event.currentTarget.setPointerCapture(event.pointerId); startTransitRepeat(1); }} onPointerUp={stopTransitRepeat} onPointerCancel={stopTransitRepeat} onPointerLeave={stopTransitRepeat} onClick={(event) => event.preventDefault()}>+ Salto</Button>
              </div>
            </Section>

            <Section>
              <FormRow>
                <Button onClick={() => handleCalculate(true)}>Actualizar momento</Button>
              </FormRow>
            </Section>

            {chartData && (
              <div style={{ display: 'flex', justifyContent: 'center', marginTop: '16px', marginBottom: '16px' }}>
                <div style={{ width: chartSize, height: chartSize, backgroundColor: '#fff', borderRadius: '12px', padding: '10px' }}>
                  {useCanvas ? (
                    <ChartCanvas width={chartSize} height={chartSize} chartData={chartData} />
                  ) : (
                    <ChartSvg
                      width={chartSize}
                      height={chartSize}
                      svgContent={generateChartSvg(chartData, { width: chartSize, height: chartSize, isTransit: false })}
                    />
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </Form>
    </KonstaAppWrapper>
  );
}

export default App;
