def refactor(img):
    # Convert image from BGR to RGB format
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Extract text from the image using Tesseract
    text = pytesseract.image_to_string(img, config=config, lang='rus')
    logger.info(f'text received: {text}')

    # Get word coordinates and other details from the image
    data = pytesseract.image_to_data(img, config=config, lang='rus')

    # Find "secret words" in the extracted text
    secret_words = extract_secret_words(text)
    logger.info(f'secret words received: {secret_words}')

    # Flag to handle word continuation after hyphens or line breaks
    draw_black_rect = False

    # Counter for the number of drawn rectangles
    rectangle_count = 0

    # Counter for the number of "secret words"
    secret_word_count = len(secret_words)

    for i, line in enumerate(data.splitlines()):
        if i == 0:
            # Skip first iteration
            continue

        elements = line.split()
        if len(elements) < 12:
            # Skip lines that do not have enough elements
            logger.warning('Operation skipped due to insufficient elements')
            continue

        # Extract coordinates and dimensions for drawing rectangles
        x, y, w, h = map(int, elements[6:10])
        current_word = clean_word(elements[11].lower())

        if draw_black_rect:
            # Draw a black rectangle over the previous word if needed
            cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)
            logger.info(f'the rectangle is drawn (hyphenation), coordinates: {x, y, w, h}')
            draw_black_rect = False
            rectangle_count += 1  # Increment the rectangle counter

        for word in secret_words:
            # Check if the current word matches a "secret word"
            if current_word == word.group(31).lower():
                # Draw a black rectangle over the matched word
                cv2.rectangle(img, (x, y), (w + x, h + y), (0, 0, 0), thickness=-1)
                logger.info(f'the rectangle is drawn, coordinates: {x, y, w, h}')
                rectangle_count += 1  # Increment the rectangle counter

                # Check for hyphenation or line breaks to continue
                if current_word.endswith(('-', '—')) or word.group(33) == '\n':
                    draw_black_rect = True

    # Log the total number of rectangles drawn
    logger.info(f'Total rectangles drawn: {rectangle_count}')
    logger.info(f'Total secret words found: {secret_word_count}')

    # Compare the number of rectangles with the number of secret words
    if rectangle_count == secret_word_count:
        logger.info("The number of rectangles matches the number of secret words.")
    else:
        logger.warning("The number of rectangles does NOT match the number of secret words.")

    return img