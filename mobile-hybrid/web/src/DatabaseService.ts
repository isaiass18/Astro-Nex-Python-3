import initSqlJs from 'sql.js';
import type { Database } from 'sql.js';

let db: Database | null = null;
let initPromise: Promise<void> | null = null;

export async function initDatabase() {
  if (db) return;
  if (initPromise) return initPromise;

  initPromise = (async () => {
    try {
      const SQL = await initSqlJs({
        locateFile: file => `/${file}`
      });
      const response = await fetch('/data/local.db');
      const buffer = await response.arrayBuffer();
      db = new SQL.Database(new Uint8Array(buffer));
      console.log('Base de datos offline cargada con éxito (sql.js)');
    } catch (err) {
      console.error('Error al inicializar la base de datos local:', err);
    }
  })();

  return initPromise;
}

function normalizeSearch(str: string): string {
  return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

function normalizedSqlColumn(column: string): string {
  // Simple SQLite replacement mimicking the python implementation.
  // Actually, since we do this in JS, we can just fetch all or we can use LIKE 
  // but standard sqlite LIKE is case-insensitive (ASCII). 
  // To avoid complex SQL REPLACE chains, we can just fetch countries 
  // and filter in memory if the dataset is small.
  // The worldnames table has 250 rows, easy to filter in memory!
  return `replace(replace(replace(replace(replace(replace(replace(lower(${column}),'á','a'),'é','e'),'í','i'),'ó','o'),'ú','u'),'ü','u'),'ñ','n')`;
}

export async function searchCountries(query: string, limit: number = 12) {
  await initDatabase();
  if (!db) return [];
  
  const normQuery = normalizeSearch(query).trim();
  if (normQuery.length < 2) return [];

  // Use the same replace pattern as the python backend for SQL query
  const sql = `SELECT code, name FROM worldnames WHERE ${normalizedSqlColumn('name')} LIKE ? ORDER BY name LIMIT ?`;
  
  const results: any[] = [];
  try {
    const stmt = db.prepare(sql);
    stmt.bind([`%${normQuery}%`, limit]);
    while (stmt.step()) {
      const row = stmt.getAsObject();
      results.push({ id: row.code, code: row.code, name: row.name });
    }
    stmt.free();
  } catch (err) {
    console.error(err);
  }
  return results;
}

export async function searchLocations(query: string, countryCode: string, limit: number = 12) {
  await initDatabase();
  if (!db) return [];
  
  const normQuery = normalizeSearch(query).trim();
  if (normQuery.length < 2) return [];

  // Read worldadmin for region mapping (optional if we need full region names, but we just need AC and coordinates)
  // Let's query the specific country table:
  const tableName = countryCode; // The table is named after the country code e.g. "CO", "ES", "US"
  
  const results: any[] = [];
  try {
    const sql = `SELECT Ciudad, AC, Latitud, Longitud FROM "${tableName}" WHERE ${normalizedSqlColumn('Ciudad')} LIKE ? LIMIT ?`;
    const stmt = db.prepare(sql);
    stmt.bind([`%${normQuery}%`, limit]);
    while (stmt.step()) {
      const row = stmt.getAsObject();
      
      // Astronex uses string representations for coords like " 4 38N" " 74 5W".
      // We need to parse them to decimals as the original python backend did.
      let latdec = 0;
      let londec = 0;
      
      if (typeof row.Latitud === 'number') {
         latdec = row.Latitud;
         londec = row.Longitud as number;
      } else {
         const latStr = (row.Latitud as string).trim();
         const lonStr = (row.Longitud as string).trim();
         
         // Parse Lat: e.g. " 4 38N" or "34 35S"
         const latMatch = latStr.match(/(-?\d+)\s+(\d+)([NS]?)/);
         if (latMatch) {
            let deg = parseInt(latMatch[1]);
            let min = parseInt(latMatch[2]);
            let sign = latMatch[3] === 'S' || latStr.includes('-') ? -1 : 1;
            if (deg < 0) { deg = Math.abs(deg); sign = -1; }
            latdec = sign * (deg + min / 60.0);
         }
         
         const lonMatch = lonStr.match(/(-?\d+)\s+(\d+)([EW]?)/);
         if (lonMatch) {
            let deg = parseInt(lonMatch[1]);
            let min = parseInt(lonMatch[2]);
            let sign = lonMatch[3] === 'W' || lonStr.includes('-') ? -1 : 1;
            if (deg < 0) { deg = Math.abs(deg); sign = -1; }
            londec = sign * (deg + min / 60.0);
         }
      }
      
      results.push({
        id: `${countryCode}|${row.AC}|${row.Ciudad}`,
        city: row.Ciudad,
        region: row.AC,
        country: countryCode,
        latitude: latdec,
        longitude: londec
      });
    }
    stmt.free();
  } catch (err) {
    console.error('Table might not exist or error querying:', err);
  }
  return results;
}
