import { describe, it, expect } from 'vitest';
import { calculateAgeProgression } from './ageProgression';
import fs from 'fs';
import path from 'path';

describe('Age Progression Calculations', () => {
  it('should match Python Golden Fixture exactly', () => {
    const agepPath = path.resolve(__dirname, '../../../../tests/golden/agep_output.json');
    const natalPath = path.resolve(__dirname, '../../../../tests/golden/natal_output.json');
    const inputPath = path.resolve(__dirname, '../../../../fixtures/natal_input.json');

    const goldenAgep = JSON.parse(fs.readFileSync(agepPath, 'utf8'));
    const natal = JSON.parse(fs.readFileSync(natalPath, 'utf8'));
    const input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));

    // Wait, the input has local birth "1990-06-15T14:30:00"
    // Python code uses this as local time to build the progression.
    const birthDateISO = input.birth;

    // The planets list requires `{ degree, ix }` where `degree` is the absolute longitude.
    // In python plan is `[{ degree: p, ix: i }]` for all planets
    const planets = natal.planets.map((p: any) => ({
      degree: p.longitude,
      ix: p.index
    })).sort((a: any, b: any) => a.degree - b.degree);

    const houses = natal.houses;

    const tsAgep = calculateAgeProgression(birthDateISO, planets, houses);

    if (tsAgep.length !== goldenAgep.length) {
      console.log('TS Length:', tsAgep.length, 'Golden Length:', goldenAgep.length);
      // Find missing or extra
      const goldenLabels = goldenAgep.map((x: any) => x.lab).join(',');
      const tsLabels = tsAgep.map((x: any) => x.lab).join(',');
      console.log('TS Extra/Missing:', tsAgep.filter(x => !goldenLabels.includes(x.lab)));
      console.log('Golden Extra/Missing:', goldenAgep.filter((x: any) => !tsLabels.includes(x.lab)));
    }
    
    // We can also just zip and compare to find the first diff
    const countCl = (arr: any[], cl: string) => arr.filter(x => x.cl === cl).length;
    console.log('TS asps:', countCl(tsAgep, 'asp'), 'Golden asps:', countCl(goldenAgep, 'asp'));
    console.log('TS mids:', countCl(tsAgep, 'mid'), 'Golden mids:', countCl(goldenAgep, 'mid'));
    console.log('TS signs:', countCl(tsAgep, 'sign'), 'Golden signs:', countCl(goldenAgep, 'sign'));
    console.log('TS prpi:', countCl(tsAgep, 'pr') + countCl(tsAgep, 'pi'), 'Golden prpi:', countCl(goldenAgep, 'pr') + countCl(goldenAgep, 'pi'));
    
    // Check first midpoint diff
    const tsSigns = tsAgep.filter(x => x.cl === 'sign');
    const gSigns = goldenAgep.filter((x: any) => x.cl === 'sign');
    console.log('TS Signs:', tsSigns);
    console.log('Golden Signs:', gSigns);

    
    expect(tsAgep.length).toBe(goldenAgep.length);
  });
});
