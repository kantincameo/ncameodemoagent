# Form 1040 → documents to request

> `scripts/build_checklist.py` applies this mapping in code; this page explains it. If you change one, change both.

Use the prior-year Form 1040 and its schedules to decide what the client must upload for the year being
prepared. Request a document only when the line is non-zero, the schedule or form is attached, or the client
told you about a change. One checklist item per issuer where the return names one.

## Income
| 1040 line / schedule | Document to request | DocumentType |
| --- | --- | --- |
| 1a wages, salaries, tips | W-2 from each employer | `W-2` |
| 1b–1h (household wages, tip income, Medicaid waiver, dependent-care benefits, adoption benefits, Form 8919) | W-2 / employer statement for that item | `W-2` |
| 2a tax-exempt interest, 2b taxable interest; Schedule B Part I | 1099-INT from each bank or broker (1099-OID if listed) | `1099-INT` |
| 3a qualified, 3b ordinary dividends; Schedule B Part II | 1099-DIV from each broker or fund | `1099-DIV` |
| 4a/4b IRA distributions | 1099-R from each IRA custodian; Form 8606 basis records if a nondeductible IRA | `1099-R` |
| 5a/5b pensions and annuities | 1099-R from each payer | `1099-R` |
| 6a/6b Social Security benefits | SSA-1099 (RRB-1099 for railroad retirement) | `SSA-1099` |
| 7 capital gain or loss; Schedule D; Form 8949 | 1099-B (consolidated 1099) from each broker; cost basis for anything not reported; crypto exchange statements | `1099-B` |
| Schedule 1 line 1 taxable state refund | 1099-G from the state | `1099-G` |
| Schedule 1 line 2a alimony received | Divorce decree / payment records (agreements before 2019) | `Alimony` |
| Schedule 1 line 3; Schedule C business income | 1099-NEC, 1099-K and 1099-MISC from each payer; income and expense records; mileage log; home-office details | `Schedule C records` |
| Schedule 1 line 4; Form 4797 sale of business property | Sale documents and depreciation records | `Form 4797 records` |
| Schedule 1 line 5; Schedule E Part I rentals or royalties | Rent received, expenses, 1098 for each rental property, property tax, 1099-MISC royalties | `Schedule E records` |
| Schedule E Part II partnerships, S corporations, trusts | Schedule K-1 from each entity | `K-1` |
| Schedule 1 line 6; Schedule F farm income | Farm income and expense records, 1099-G / CCC payments | `Schedule F records` |
| Schedule 1 line 7 unemployment compensation | 1099-G | `1099-G` |
| Schedule 1 line 8 other income (gambling, prizes, jury duty, HSA/529 distributions) | W-2G, 1099-MISC, 1099-SA, 1099-Q as applicable | as applicable |

## Adjustments, deductions and credits
| 1040 line / schedule / form | Document to request | DocumentType |
| --- | --- | --- |
| Schedule 1 line 11 educator expenses | Receipts for classroom supplies | `Educator expenses` |
| Schedule 1 line 13; Form 8889 HSA | 1099-SA and 5498-SA; W-2 box 12 code W | `5498-SA` |
| Schedule 1 line 15 self-employment tax / line 16 SEP, SIMPLE, solo 401(k) | Retirement contribution statements | `Retirement contributions` |
| Schedule 1 line 17 self-employed health insurance | Premium statements | `Health insurance premiums` |
| Schedule 1 line 20 IRA deduction | 5498 or contribution confirmation | `5498` |
| Schedule 1 line 21 student loan interest | 1098-E from each lender | `1098-E` |
| Schedule A line 1 medical expenses | Medical and dental bills, insurance premiums paid | `Medical expenses` |
| Schedule A line 5 state and local taxes | Property tax bills; vehicle registration (if deductible); state estimated payments | `Property tax` |
| Schedule A line 8 mortgage interest | 1098 from each lender | `1098` |
| Schedule A lines 11–12 charitable gifts | Donation receipts / acknowledgment letters; Form 8283 records for non-cash gifts over $500 | `Charitable receipts` |
| Form 2441 child and dependent care credit | Provider name, address, EIN/SSN on file and amount paid (statement from each provider); W-2 box 10 | `Childcare statement` |
| Form 8863 education credits | 1098-T from each school; tuition and book receipts | `1098-T` |
| Form 8962 premium tax credit | 1095-A from the Marketplace | `1095-A` |
| Form 5695 residential energy credits | Invoices for qualifying improvements | `Energy improvements` |
| Form 8936 clean vehicle credit | Purchase agreement and dealer time-of-sale report | `Clean vehicle` |
| Form 8839 adoption credit | Adoption expense records | `Adoption expenses` |

## Payments
| 1040 line | Document to request | DocumentType |
| --- | --- | --- |
| 25a–25c federal income tax withheld | Covered by the W-2s and 1099s above | — |
| 26 estimated tax payments and amount applied from last year | Dates and amounts of each federal estimated payment (and state) | `Estimated payments` |
| 34/35a refund to bank account, or 37 amount owed | Bank account for refund or payment (routing and account number go in the client's secure form, never in a task) | `Bank account` |

## Life changes to ask about
A change since the prior return can add or remove documents: new or lost job, marriage or divorce, new
dependent, move to another state (part-year state returns), home bought or sold (closing statement),
started a business, retirement distributions started, IRS letters received. If the client mentions one,
add the matching item with `Source: "base"`.
