package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"
	"github.com/atotto/clipboard"
)

type AllocationCalculator struct {
	currentBalances []float64
	infoTable       [][]string
	targetValues    []float64
	filename        string
}

func (ac *AllocationCalculator) scrapeValuesFromCSV(filename string) error {
	file, err := os.Open(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return err
	}

	ac.currentBalances = nil
	ac.infoTable = [][]string{
		{"Symbol", "Current Value", "Current Allocation", "Target Value", "Target Allocation"},
	}

	for i := 2; i < 5; i++ {
		valueStr := strings.Trim(records[i][7], "$")
		value, err := strconv.ParseFloat(valueStr, 64)
		if err != nil {
			return err
		}
		ac.currentBalances = append(ac.currentBalances, value)
		ac.infoTable = append(ac.infoTable, []string{records[i][2], valueStr})
	}

	return nil
}

func (ac *AllocationCalculator) buyOrSell(percentage, total, current, moneyToInvest float64, name string) string {
	target := total * percentage
	actualVsTargetRatio := target / current

	var action string
	if 0.95 < actualVsTargetRatio && actualVsTargetRatio < 1.05 && int(moneyToInvest) == 0 {
		action = fmt.Sprintf("Looks good for %s", name)
	} else {
		amountToTrade := target - current
		if amountToTrade > 0 {
			action = fmt.Sprintf("Buy $%.2f %s", amountToTrade, name)
		} else {
			action = fmt.Sprintf("Sell $%.2f %s", -amountToTrade, name)
		}
	}
	ac.targetValues = append(ac.targetValues, target)
	return action
}

func (ac *AllocationCalculator) calculateStrategy(moneyToInvest float64) (string, error) {
	var bondPercentage, intlPercentage, nationalPercentage float64
	switch {
	case strings.Contains(ac.filename, "202"):
		bondPercentage, intlPercentage, nationalPercentage = 0.1, 0.3, 0.6
	case strings.Contains(ac.filename, "203"):
		bondPercentage, intlPercentage, nationalPercentage = 0.3, 0.27, 0.43
	default:
		bondPercentage, intlPercentage, nationalPercentage = 1.0, 0.0, 0.0
	}

	totalAmount := moneyToInvest
	for _, balance := range ac.currentBalances {
		totalAmount += balance
	}

	result := strings.Builder{}
	result.WriteString(fmt.Sprintf("Current Amount In Bonds: %.2f\n", ac.currentBalances[0]))
	result.WriteString(fmt.Sprintf("Current Amount In International Index: %.2f\n", ac.currentBalances[1]))
	result.WriteString(fmt.Sprintf("Current Amount In National Index: %.2f\n", ac.currentBalances[2]))
	result.WriteString(fmt.Sprintf("Bond Strategy: %s\n",
		ac.buyOrSell(bondPercentage, totalAmount, ac.currentBalances[0], moneyToInvest, "Bonds")))
	result.WriteString(fmt.Sprintf("Intl Strategy: %s\n",
		ac.buyOrSell(intlPercentage, totalAmount, ac.currentBalances[1], moneyToInvest, "International Index")))
	result.WriteString(fmt.Sprintf("National Strategy: %s\n",
		ac.buyOrSell(nationalPercentage, totalAmount, ac.currentBalances[2], moneyToInvest, "National Index")))

	return result.String(), nil
}

func main() {
	app := app.New()
	window := app.NewWindow("Asset Allocation")

	ac := &AllocationCalculator{}

	csvLabel := widget.NewLabel("No CSV file selected")
	investmentInput := widget.NewEntry()
	investmentInput.SetPlaceHolder("Enter amount to invest")

	strategyLabel := widget.NewLabel("")

	selectCSVButton := widget.NewButton("Select CSV", func() {
		dialog.ShowFileOpen(func(reader fyne.URIReadCloser, err error) {
			if err != nil || reader == nil {
				return
			}
			filename := reader.URI().Path()
			csvLabel.SetText(filepath.Base(filename))
			ac.filename = filename
			if err := ac.scrapeValuesFromCSV(filename); err != nil {
				log.Println("Error reading CSV:", err)
			}
		}, window)
	})

	calculateButton := widget.NewButton("Calculate Strategy", func() {
		investment, err := strconv.ParseFloat(investmentInput.Text, 64)
		if err != nil {
			strategyLabel.SetText("Invalid investment amount")
			return
		}
		result, err := ac.calculateStrategy(investment)
		if err != nil {
			strategyLabel.SetText("Error calculating strategy")
			return
		}
		strategyLabel.SetText(result)
	})

	copyButton := widget.NewButton("Copy Strategy", func() {
		_ = clipboard.WriteAll(strategyLabel.Text)
	})

	content := container.NewVBox(
		csvLabel,
		selectCSVButton,
		investmentInput,
		calculateButton,
		strategyLabel,
		copyButton,
	)

	window.SetContent(content)
	window.Resize(fyne.NewSize(1280, 720))
	window.ShowAndRun()
}
