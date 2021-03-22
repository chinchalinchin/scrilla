// Angular Core Imports
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';

// Custom Component Imports
import { AppComponent } from './app.component';
import { AnalysisComponent } from './tabs/analysis/analysis.component';
import { ArgumentsComponent } from './input/args/arguments.component';
import { PortfolioComponent } from './input/portfolio/portfolio.component';
import { OptimizerComponent } from './widgets/optimizer/optimizer.component';
import { EfficientFrontierComponent } from './widgets/efficient-frontier/efficient-frontier.component';

// Angular Material Imports
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';
import { MatTabsModule } from '@angular/material/tabs';
import { MatListModule } from '@angular/material/list';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';




// Third Party Material
import  { MatCurrencyFormatModule } from 'mat-currency-format';
import { ValuationComponent } from './widgets/valuation/valuation.component';



@NgModule({
  declarations: [
    AppComponent,
    OptimizerComponent,
    ArgumentsComponent,
    PortfolioComponent,
    AnalysisComponent,
    EfficientFrontierComponent,
    ValuationComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    FormsModule,
    HttpClientModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatInputModule,
    MatTableModule,
    MatFormFieldModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatGridListModule,
    MatSelectModule,
    MatRadioModule,
    MatTabsModule,
    MatListModule,
    MatCurrencyFormatModule,
    MatProgressBarModule,
    MatChipsModule,
    ReactiveFormsModule,
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
