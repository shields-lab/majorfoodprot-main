import csv
with open('Food_peptide_database-input.csv', newline='', encoding='utf-8') as f_in, \
     open('Food_peptide_database-input.tsv', 'w', newline='', encoding='utf-8') as f_out:
    reader = csv.reader(f_in)
    writer = csv.writer(f_out, delimiter='\t')
    writer.writerows(reader)
