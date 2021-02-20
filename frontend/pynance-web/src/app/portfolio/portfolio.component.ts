import { Component, Input, OnInit, SimpleChanges } from '@angular/core';
import { Holding } from 'src/app/models/holding';
import { containsObject, removeStringFromArray } from 'src/utilities';

const mockPortfolio : Holding[] = [
  { ticker: 'ALLY', allocation: 0.2 },
  { ticker: 'BX', allocation: 0.25 },
  { ticker: 'SNE', allocation: 0.4 },
  { ticker: 'PFE', allocation: 0.1 },
  { ticker: 'TWTR', allocation: 0.05 }
]

@Component({
  selector: 'app-portfolio',
  templateUrl: './portfolio.component.html'
})
/**
 * PortfolioComponent
 * 
 * Input
 * 1. tickers [string]
 * 2. allocations: [number]. An array of proportions  
 */
export class PortfolioComponent implements OnInit {

  private clearDisabled : boolean = false;
  private portfolio : Holding[] = [];
  
  @Input()
  private allocations: number[]

  displayedColumns: string[];

  constructor() { }

  ngOnInit() {  } 

  
  ngOnChanges(changes: SimpleChanges) {
    if (changes.allocations) {
      
      if(this.portfolio.length != 0){
        // empty portfolio passed in
        if(changes.allocations.currentValue.length == 0){ 
          this.displayedColumns = ['ticker']
          for(let holding of this.portfolio){
            holding.allocation = null;
          }
        }
        // allocation portfolio passed in
        else{
          this.displayedColumns = ['ticker', 'allocation']
          for(let newAllocation of changes.allocations.currentValue){
            let tickerIndex=changes.allocations.currentValue.indexOf(newAllocation)
            this.portfolio[tickerIndex].allocation = newAllocation
          }
        }

    }
    }
  }

  public setTickers(tickers: string[]){
    for(let ticker of tickers){ console.log(`tickers ${ticker}`)}

    for(let holding of this.portfolio){
      if(containsObject(holding.ticker, tickers)){
        removeStringFromArray(holding.ticker, tickers)
      }
    }
    
    for(let ticker of tickers){ console.log(`tickers ${ticker}`)}

    for(let ticker of tickers){
      this.portfolio.push({ ticker: ticker, allocation: null})
    }
  }

  public setAllocations(allocations : number[]){
    for(let portion of allocations){
      let thisIndex : number = allocations.indexOf(portion)
      this.portfolio[thisIndex].allocation = portion
    }
  }

}
