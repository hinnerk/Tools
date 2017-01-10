import io, console, appex, clipboard
import convert

    
if __name__ == '__main__':
    source = appex.get_file_path()
    try:
        raw_data = open(source, 'rb').read()
        raw_data = convert.convert_unicode(raw_data)
        raw_data = raw_data.strip()
        converted_data = convert.convert(raw_data)
        b = io.StringIO()
        convert.write_result(converted_data, b)
        clipboard.set(b.getvalue())
        b.close()
    except FileNotFoundError:
        console.hud_alert('No such file: "{}"'.format(source), 'error')
        #sys.exit(42)
    except ConverterNotFound:
        console.hud_alert('File type detection failed :(', 'error')
        #sys.exit(110)
    else:
        console.hud_alert("Conversion successfull!\nData copied to clipboard.", 'success')
        # sys.exit(0)
