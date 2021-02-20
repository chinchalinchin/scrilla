import { MatTable } from '@angular/material';
import { Component, Input, OnInit, SimpleChanges, ViewChild } from '@angular/core';
import { Holding } from 'src/app/models/holding';
import { containsObject, removeStringFromArray } from 'src/utilities';

const mockPortfolio : Holding[] = [
  { index: 1, ticker: 'ALLY', allocation: 0.2 },
  { index: 2, ticker: 'BX', allocation: 0.25 },
  { index: 3, ticker: 'SNE', allocation: 0.4 },
  { index: 4, ticker: 'PFE', allocation: 0.1 },
  { index: 5, ticker: 'TWTR', allocation: 0.05 }
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

  private clearDisabled : boolean = true;
  private portfolio : Holding[] = [];
  private displayedColumns: string[] = [];

  @ViewChild('portfolioTable', {static: false})
  private portfolioTable : MatTable<Holding[]>;
  

  
  @Input()
  private allocations: number[]

  constructor() { }

  ngOnInit() {  } 

  
  ngOnChanges(changes: SimpleChanges) {
    if (changes.allocations) {
      if(this.portfolio.length != 0){
        // empty portfolio passed in
        if(changes.allocations.currentValue.length == 0){ 
          this.displayedColumns = ['index', 'ticker']
          for(let holding of this.portfolio){
            holding.allocation = null;
          }
        }
        // allocation portfolio passed in
        else{
          this.displayedColumns = ['index', 'ticker', 'allocation']
          for(let newAllocation of changes.allocations.currentValue){
            let tickerIndex=changes.allocations.currentValue.indexOf(newAllocation)
            this.portfolio[tickerIndex].allocation = newAllocation
          }
        }
      }
    }

  }

  public setTickers(tickers: string[]) : void{
    for(let holding of this.portfolio){
      if(containsObject(holding.ticker, tickers)){
        removeStringFromArray(holding.ticker, tickers)
      }
    }

    for(let ticker of tickers){
      let newIndex = this.portfolio.length+1;
      this.portfolio.push({ index: newIndex, ticker: ticker, allocation: null})
    }
  
    if(this.portfolio.length != 0){
      this.clearDisabled = false;
      this.displayedColumns = ['index', 'ticker']
    }

    this.portfolioTable.renderRows()
  }

  public setAllocations(allocations : number[]) : void{
    for(let portion of allocations){
      let thisIndex : number = allocations.indexOf(portion)
      this.portfolio[thisIndex].allocation = portion
    }
  }

  public clearPortfolio():void{
    this.portfolio = [];
    this.clearDisabled = true;
    this.displayedColumns = [];
  }

}
