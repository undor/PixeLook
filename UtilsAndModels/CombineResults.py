def make_better_result():
    in_fname = "Results/try.csv"
    csv_file = open("Results/ForChangeRes.csv", "a")

    result=[]
    cnt_p=0
    line_location=0
    with open(in_fname) as f:
        lines = f.read().splitlines()
        line_location = 0
        lines_num = len(lines)
        while line_location < lines_num:
            line_data = lines[line_location].split(',')
            if line_data[0][0] == 'p':
                cnt_p+=1
                line_location+=1
                continue
            if(line_data[6][0]!='T' and line_data[6][1]!='T'):
                print("line num is",line_location)
                print("no!!!!")
                break
            next_line_data = lines[line_location+1].split(',')
            err_mm_x = float(line_data[3])
            err_mm_y = float(next_line_data[4])
            err_mm = np.sqrt(err_mm_x**2 + err_mm_y**2)
            line_location = line_location + 2
            if (err_mm_x > 450 or err_mm_y > 450):
                continue
            csv_file.write(str(str(err_mm_x)+","+str(err_mm_y)+","+str(err_mm)+"\n"))
            csv_file.flush()


    csv_file.close()
    print("all headers are ",cnt_p)