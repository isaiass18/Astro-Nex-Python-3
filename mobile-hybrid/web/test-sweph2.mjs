import sweph from 'sweph-wasm';

async function test() {
  const sw = new sweph();
  // 1990-06-15 19:30:00 UTC
  const jd = sw.swe_julday(1990, 6, 15, 19.5, 1);
  console.log("JD:", jd);
  
  const calc = sw.swe_calc_ut(jd, 0, 2); // Sun
  console.log("Sun:", calc);
}

test();
