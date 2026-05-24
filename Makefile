.PHONY: help install generate clean lint

help:
	@echo ""
	@echo "  AI Tools Faceless Channel — PDF Generator"
	@echo ""
	@echo "  Available commands:"
	@echo "    make install    Install Python dependencies"
	@echo "    make generate   Generate the PDF"
	@echo "    make clean      Remove generated PDF and cache files"
	@echo "    make lint       Run code style checks"
	@echo ""

install:
	pip install -r requirements.txt

generate:
	python generate_pdf.py

clean:
	rm -f AI_Tools_Faceless_Channel_Scripts.pdf
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

lint:
	pip install flake8 --quiet
	flake8 generate_pdf.py --max-line-length=120 --ignore=E501
