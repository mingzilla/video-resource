## Be careful about tags

- `<td>`, `<th>`
- may not close
- line break concerns
- de-latex

## Problems

### latex

```text
<table><tr><td>From Date</td><td> $\sqrt[d]{2}$ </td><td> $\sqrt[d]{4}$ </td><td> $\sqrt[m]{0}$ </td><td> $\sqrt[m]{5}$ </td><td> $\sqrt[y]{2}$ </td><td> $\sqrt[y]{0}$ </td><td> $\sqrt[y]{1}$ </td><td> $\sqrt[y]{8}$ </td></tr><tr><td>To Date</td><td> $\sqrt[d]{d}$ </td><td> $\sqrt[d]{d}$ </td><td> $\sqrt[m]{m}$ </td><td> $\sqrt[m]{m}$ </td><td> $\sqrt{y}$ </td><td> $\sqrt{y}$ </td><td> $\sqrt{y}$ </td><td> $\sqrt{y}$ </td></tr></table>
```

expect: `From Date d 1 d 5 m 0 m 1 y 2 y 0 y 1 y 8 (= 15/01/2018)`

### td/th

- `<td>1</td><td>0</td><td>9</td>` -> `109`
- `<td>From</td><td>Date</td><td>X</td>` -> `FromDateX`
- (Don't just pad space) -> `From Date X` -- which way? `(From Date) X` or `From (Date X)`?
- be careful about `<td colspan=2>`

## Solution

- Do this one thing solves all: `</td>` -> ` </td> |`
- Very close, but no, typically miss closing, but not miss opening
- so doe the two below then:
    - `<td>` -> `| <td>`
    - `<td ` -> `| <td `
    - this is to avoid genuine `<td` something for different purposes

## Clean procedure

```
ocr text -> de-latex -> pad td/th -> (existing procedure: normal style cleaning etc)
non ocr ->           -> pad td/th -> (existing procedure: normal style cleaning etc)
```
