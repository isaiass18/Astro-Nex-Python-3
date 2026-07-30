import SwissEPH from 'sweph-wasm';

async function test() {
  try {
    const swe = await SwissEPH.init();
    
    // Test for 1990-06-15 14:30 Bogota (-05:00) => 1990-06-15 19:30 UTC
    const jd = swe.swe_julday(1990, 6, 15, 19.5, 1);
    console.log("JD:", jd);
    
    // Sun
    const sun = swe.swe_calc_ut(jd, 0, 0); // Sun = 0
    console.log("Sun Longitude:", sun[0], "Lat:", sun[1]);
  } catch (err) {
    console.error("Error:", err);
  }
}

test();
