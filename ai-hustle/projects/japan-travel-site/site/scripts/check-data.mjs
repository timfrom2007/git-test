// 檢查票價資料：每筆有數字的資料都必須附來源；沒有數字的必須標 unknown。
import fs from 'node:fs';
const d = JSON.parse(fs.readFileSync(new URL('../src/data/fares.json', import.meta.url)));
let bad = 0;
for (const x of [...d.passes, ...d.routes]) {
  const hasNum = (x.fare ?? x.priceOfficialSite) != null;
  if (hasNum && (!x.sources || x.sources.length === 0)) { console.error('缺來源:', x.id); bad++; }
  if (!hasNum && x.confidence !== 'unknown') { console.error('無數字但未標 unknown:', x.id); bad++; }
}
const ids = new Set(d.routes.map(r => r.id));
for (const p of d.passes) for (const c of p.covers) if (!ids.has(c)) { console.error('未知路線', p.id, c); bad++; }
console.log(bad ? `${bad} 個問題` : `OK：${d.passes.length} 張票券、${d.routes.length} 條路線，查核日 ${d.checked}`);
process.exit(bad ? 1 : 0);
