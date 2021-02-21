import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-analysis',
  templateUrl: './analysis.component.html'
})
export class AnalysisComponent implements OnInit {
  public explanations : boolean = false;

  constructor() { }

  ngOnInit(): void {
  }

}
